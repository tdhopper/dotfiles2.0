#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "google-genai>=2.7",
# ]
# ///
"""Carefully transcribe a scanned historical PDF with Gemini.

Pipeline (one page at a time, for max resolution + resumability):
  1. Render each PDF page to a high-res PNG (pdftoppm).
  2. Optionally enhance faded carbon copies (ImageMagick: grayscale,
     deskew, contrast stretch) -- big win on low-contrast scans.
  3. Send the page image to Gemini with a strict, verbatim
     historical-transcription prompt (temperature 0, high media
     resolution, minimal thinking -- the SOTA settings for OCR/HTR).
  4. Save one Markdown file per page (with metadata front-matter) plus a
     combined file, and a manifest flagging pages that need human review.

Resumable: already-transcribed pages are skipped unless --force.

Usage:
  uv run scripts/transcribe_documents.py INPUT.pdf
  uv run scripts/transcribe_documents.py INPUT.pdf -o out/ -m gemini-3-pro-preview
  uv run scripts/transcribe_documents.py INPUT.pdf --pages 5,7-9 --force
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from google import genai
from google.genai import types

# --- Document context -------------------------------------------------------
# Context helps Gemini disambiguate proper nouns / period spellings; the model
# is told to use it ONLY for disambiguation, never to invent text. Supply it
# per-document with --context "..." or --context-file PATH. The more specific
# (names, places, dates, document type, era-specific spellings or currencies),
# the better the accuracy on hard-to-read words. Empty context still works.
#
# Example of a good context block:
#   - Typewritten carbon copies, September 1956.
#   - Author: Joe B. Hopper, a missionary writing from Chunju, Korea.
#   - Recipient: Dr. L. Nelson Bell, Montreat, North Carolina.
#   - The Korean currency "hwan" is spelled "whan"; keep it as written.
DEFAULT_CONTEXT = "(No specific document context was provided.)"

PROMPT_TEMPLATE = """\
You are transcribing a scanned historical document for an archive. This is page \
{page} of {total}. The source may be handwritten, typewritten, or printed, and \
may be a faded carbon copy, low-contrast, skewed, or rotated -- read the text in \
its correct reading orientation no matter how the image is oriented.

Context to help you resolve genuinely ambiguous characters (use ONLY to \
disambiguate -- never copy text out of this list and never invent content from \
it):
{context}

Transcription rules:
1. Transcribe ALL text VERBATIM, exactly as it appears. Preserve the original \
spelling, capitalization, punctuation, abbreviations, typographical errors, and \
line breaks.
2. Do NOT correct, modernize, paraphrase, summarize, translate, or comment.
3. Work carefully, character by character, to minimize character/word error rate.
4. For any word or character you cannot read confidently, write [illegible], or \
[illegible: best guess] if you have a plausible reading. NEVER invent or \
hallucinate text to fill a gap.
5. Include headers, footers, page numbers, and any handwritten annotations or \
marginalia. Tag handwriting as [handwritten: ...] and margin notes as \
[margin: ...].
6. Reproduce paragraph structure; separate paragraphs with a blank line.
7. If the page is blank or has no legible text, output exactly: [no legible text]

Output the transcription first. Then, on the VERY LAST line and nothing after \
it, output a single-line JSON object describing this page:
{{"confidence": "high|medium|low", "illegible_count": <int>, \
"rotation_observed": "none|90cw|90ccw|180|other", "notes": "<short note>"}}"""

META_RE = re.compile(r"\{[^{}]*\"confidence\"[^{}]*\}\s*$")


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def render_page(pdf: Path, page: int, dpi: int, workdir: Path) -> Path:
    """Render a single PDF page to PNG via pdftoppm."""
    out_prefix = workdir / f"page-{page:03d}"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), "-f", str(page), "-l", str(page),
         str(pdf), str(out_prefix)],
        check=True, capture_output=True,
    )
    # pdftoppm appends -NN (zero-padded to total page-count width); find it.
    matches = sorted(workdir.glob(f"page-{page:03d}*.png"))
    if not matches:
        raise FileNotFoundError(f"pdftoppm produced no PNG for page {page}")
    return matches[0]


def enhance(png: Path) -> Path:
    """Enhance a faded scan with ImageMagick. No-op if magick is missing."""
    magick = "magick" if have("magick") else ("convert" if have("convert") else None)
    if magick is None:
        return png
    out = png.with_name(png.stem + "-enh.png")
    cmd = [magick, str(png)] if magick == "magick" else [magick, str(png)]
    cmd += [
        "-auto-orient",
        "-colorspace", "Gray",
        "-deskew", "40%",
        "-contrast-stretch", "2%x1%",  # pull faded carbon toward black/white
        "-normalize",
        str(out),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return out
    except subprocess.CalledProcessError:
        return png  # fall back to the raw render


def split_meta(text: str) -> tuple[str, dict]:
    """Peel the trailing JSON metadata line off the transcription."""
    text = text.strip()
    m = META_RE.search(text)
    meta: dict = {}
    if m:
        try:
            meta = json.loads(m.group(0))
            text = text[: m.start()].rstrip()
        except json.JSONDecodeError:
            pass
    # strip an accidental ```...``` fence if the model added one
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    return text, meta


def transcribe_page(client: genai.Client, model: str, img: Path,
                    page: int, total: int, max_tokens: int,
                    context: str = DEFAULT_CONTEXT,
                    temperature: float = 0.0,
                    retries: int = 3) -> tuple[str, dict]:
    prompt = PROMPT_TEMPLATE.format(page=page, total=total, context=context)
    img_bytes = img.read_bytes()

    # Build config; degrade gracefully if a model rejects an optional knob.
    def make_config(full: bool) -> types.GenerateContentConfig:
        kw: dict = {"temperature": temperature, "max_output_tokens": max_tokens}
        if full:
            kw["media_resolution"] = types.MediaResolution.MEDIA_RESOLUTION_HIGH
            kw["thinking_config"] = types.ThinkingConfig(thinking_budget=128)
        return types.GenerateContentConfig(**kw)

    last_err = None
    for attempt in range(retries):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    prompt,
                ],
                config=make_config(full=(attempt == 0)),
            )
            text = (resp.text or "").strip()
            if not text:
                raise RuntimeError("empty response")
            return split_meta(text)
        except Exception as e:  # noqa: BLE001 - retry on any transient error
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"page {page} failed after {retries} tries: {last_err}")


# --- Consensus / reconciliation --------------------------------------------

def _norm(text: str) -> str:
    """Collapse whitespace for agreement comparison (NOT for the saved text)."""
    return re.sub(r"\s+", " ", text).strip()


def word_disagreements(a: str, b: str, limit: int = 25) -> list[str]:
    """Human-readable list of where two transcriptions differ, word-level."""
    import difflib
    aw, bw = a.split(), b.split()
    diffs = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, aw, bw).get_opcodes():
        if tag == "equal":
            continue
        left = " ".join(aw[i1:i2]) or "∅"
        right = " ".join(bw[j1:j2]) or "∅"
        diffs.append(f"{left!r} | {right!r}")
        if len(diffs) >= limit:
            diffs.append("…(more)")
            break
    return diffs


RECONCILE_PROMPT = """\
You are reconciling {n} independent transcriptions of the SAME scanned page \
(page {page} of {total}) into one authoritative, VERBATIM transcription. I am \
giving you the page image and the candidate transcriptions. The page is \
typewritten and may be faded or rotated; read it in correct reading orientation.

Rules:
1. Decide every disputed character by RE-READING THE IMAGE -- the candidates are \
hints, not authorities.
2. VERBATIM: preserve the original spelling, typos, capitalization, punctuation, \
abbreviations, and line breaks. Do NOT modernize or "fix" the typist's errors.
3. Where candidates agree AND the image is consistent, keep that text.
4. Where they disagree, choose the reading the image supports. If the image is \
genuinely ambiguous, write [illegible: best guess] -- never invent text.
5. Same tagging as before: [handwritten: ...], [margin: ...]; "[no legible text]" \
if blank.

Candidate transcriptions:
{candidates}

Output the single reconciled transcription, then on the VERY LAST line a JSON \
object: {{"confidence": "high|medium|low", "illegible_count": <int>, \
"rotation_observed": "none|90cw|90ccw|180|other", "notes": "<short note>"}}"""


def reconcile_page(client: genai.Client, judge_model: str, img: Path,
                   candidates: list[str], page: int, total: int,
                   max_tokens: int, retries: int = 3) -> tuple[str, dict]:
    blocks = "\n\n".join(
        f"--- Candidate {chr(65 + i)} ---\n{c}" for i, c in enumerate(candidates))
    prompt = RECONCILE_PROMPT.format(
        n=len(candidates), page=page, total=total, candidates=blocks)
    img_bytes = img.read_bytes()
    last_err = None
    for attempt in range(retries):
        try:
            resp = client.models.generate_content(
                model=judge_model,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0, max_output_tokens=max_tokens,
                    media_resolution=types.MediaResolution.MEDIA_RESOLUTION_HIGH,
                    thinking_config=types.ThinkingConfig(thinking_budget=512),
                ),
            )
            text = (resp.text or "").strip()
            if not text:
                raise RuntimeError("empty response")
            return split_meta(text)
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"reconcile page {page} failed: {last_err}")


def consensus_page(client: genai.Client, voters: list[tuple[str, float]],
                   judge_model: str, img: Path, page: int, total: int,
                   max_tokens: int, context: str = DEFAULT_CONTEXT
                   ) -> tuple[str, dict]:
    """Run several transcription passes; reconcile only if they disagree."""
    cands = [transcribe_page(client, m, img, page, total, max_tokens,
                             context=context, temperature=t)
             for m, t in voters]
    texts = [c[0] for c in cands]
    if len({_norm(t) for t in texts}) == 1:
        text, meta = cands[0]
        meta["consensus"] = "unanimous"
        meta["voters"] = len(voters)
        return text, meta
    # Disagreement -> record where, then adjudicate against the image.
    diffs = word_disagreements(texts[0], texts[1]) if len(texts) >= 2 else []
    text, meta = reconcile_page(
        client, judge_model, img, texts, page, total, max_tokens)
    meta["consensus"] = "reconciled"
    meta["voters"] = len(voters)
    meta["disagreements"] = diffs
    return text, meta


def parse_pages(spec: str, total: int) -> list[int]:
    if not spec:
        return list(range(1, total + 1))
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return sorted(p for p in out if 1 <= p <= total)


def page_count(pdf: Path) -> int:
    if have("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
        for line in out.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split()[1])
    # fallback: render-probe is overkill; require pdfinfo
    raise RuntimeError("pdfinfo not found; install poppler (brew install poppler)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="output dir (default: transcriptions/<pdf-stem>/)")
    ap.add_argument("-m", "--model", default="gemini-3.1-pro-preview",
                    help="Gemini model. gemini-3.1-pro-preview (default, most "
                         "faithful on faded/rotated pages) | gemini-3.5-flash "
                         "(near-equal, cheaper) | gemini-2.5-flash (cheapest, "
                         "drops faint text -- not recommended here)")
    ap.add_argument("--consensus", action="store_true",
                    help="multi-pass: transcribe with several models, then "
                         "re-read the image to reconcile any disagreements "
                         "(~2-3x cost, fewer errors on faded pages)")
    ap.add_argument("--voters", default="gemini-3.1-pro-preview,gemini-3.5-flash",
                    help="comma-separated models for --consensus (each may add "
                         "':TEMP', e.g. 'gemini-3.1-pro-preview:0.4')")
    ap.add_argument("--judge-model", default="gemini-3.1-pro-preview",
                    help="model that adjudicates disagreements in --consensus")
    ap.add_argument("--context", default=None,
                    help="document context to help disambiguate names/spellings "
                         "(names, places, dates, era-specific terms). Used ONLY "
                         "for disambiguation, never to invent text.")
    ap.add_argument("--context-file", type=Path, default=None,
                    help="read --context from a text file instead")
    ap.add_argument("--dpi", type=int, default=300, help="render DPI (default 300)")
    ap.add_argument("--max-tokens", type=int, default=32768)
    ap.add_argument("--pages", default="", help="e.g. '5,7-9' (default: all)")
    ap.add_argument("--no-enhance", action="store_true",
                    help="skip ImageMagick contrast/deskew preprocessing")
    ap.add_argument("--force", action="store_true", help="re-transcribe existing pages")
    ap.add_argument("--keep-images", action="store_true",
                    help="keep rendered PNGs in <out>/images/")
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"error: {args.pdf} not found", file=sys.stderr)
        return 1
    if not have("pdftoppm"):
        print("error: pdftoppm not found (brew install poppler)", file=sys.stderr)
        return 1
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("error: set GEMINI_API_KEY", file=sys.stderr)
        return 1

    if args.context_file:
        context = args.context_file.read_text().strip()
    elif args.context:
        context = args.context.strip()
    else:
        context = DEFAULT_CONTEXT

    out_dir = args.output or Path("transcriptions") / args.pdf.stem
    pages_dir = out_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    img_dir = out_dir / "images"
    if args.keep_images:
        img_dir.mkdir(exist_ok=True)

    total = page_count(args.pdf)
    targets = parse_pages(args.pages, total)
    client = genai.Client(api_key=api_key)

    manifest_path = out_dir / "manifest.json"
    manifest: dict = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())

    voters: list[tuple[str, float]] = []
    if args.consensus:
        for spec in args.voters.split(","):
            spec = spec.strip()
            if not spec:
                continue
            name, _, temp = spec.partition(":")
            voters.append((name, float(temp) if temp else 0.0))
        mode_desc = (f"consensus [{', '.join(f'{m}@{t}' for m, t in voters)}] "
                     f"-> judge {args.judge_model}")
    else:
        mode_desc = args.model
    print(f"Transcribing {len(targets)}/{total} pages of {args.pdf.name} "
          f"with {mode_desc} (enhance={'off' if args.no_enhance else 'on'})\n")

    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        for page in targets:
            page_md = pages_dir / f"page-{page:03d}.md"
            if page_md.exists() and not args.force:
                print(f"  page {page:>3}: skip (exists)")
                continue
            try:
                raw = render_page(args.pdf, page, args.dpi, workdir)
                img = raw if args.no_enhance else enhance(raw)
                if args.keep_images:
                    shutil.copy(img, img_dir / f"page-{page:03d}.png")
                if args.consensus:
                    text, meta = consensus_page(
                        client, voters, args.judge_model, img, page, total,
                        args.max_tokens, context=context)
                else:
                    text, meta = transcribe_page(
                        client, args.model, img, page, total, args.max_tokens,
                        context=context)
            except Exception as e:  # noqa: BLE001
                print(f"  page {page:>3}: ERROR {e}", file=sys.stderr)
                manifest[str(page)] = {"status": "error", "error": str(e)}
                continue

            conf = meta.get("confidence", "unknown")
            illeg = meta.get("illegible_count", "?")
            cons = meta.get("consensus")
            model_line = (f"voters: {json.dumps([m for m, _ in voters])}\n"
                          f"consensus: {cons}\n") if args.consensus \
                else f"model: {args.model}\n"
            disagree = meta.get("disagreements") or []
            disagree_line = (
                "disagreements:\n" + "".join(f"  - {json.dumps(d)}\n" for d in disagree)
            ) if disagree else ""
            front = (
                f"---\npage: {page}\n{model_line}"
                f"confidence: {conf}\nillegible_count: {illeg}\n"
                f"rotation_observed: {meta.get('rotation_observed', '?')}\n"
                f"notes: {json.dumps(meta.get('notes', ''))}\n"
                f"{disagree_line}---\n\n"
            )
            page_md.write_text(front + text + "\n")
            manifest[str(page)] = {
                "status": "ok", "confidence": conf,
                "illegible_count": illeg, "chars": len(text),
                **({"consensus": cons, "disagreement_count": len(disagree)}
                   if args.consensus else {}),
            }
            tag = ""
            if args.consensus:
                tag = "  unanimous" if cons == "unanimous" \
                    else f"  reconciled({len(disagree)} diffs)"
            flag = "  <-- REVIEW" if conf in ("low", "medium", "unknown") else ""
            print(f"  page {page:>3}: {conf:>6}  illegible={illeg}  "
                  f"{len(text):>5} chars{tag}{flag}")

            manifest_path.write_text(json.dumps(manifest, indent=2))

    # Build combined file in page order from whatever exists.
    combined = out_dir / "_combined.md"
    parts = []
    for page in range(1, total + 1):
        pm = pages_dir / f"page-{page:03d}.md"
        if pm.exists():
            body = pm.read_text().split("---\n\n", 1)[-1]
            parts.append(f"\n\n----- Page {page} -----\n\n{body.rstrip()}")
    combined.write_text(f"# Transcription: {args.pdf.name}\n" + "".join(parts) + "\n")

    review = [p for p, v in manifest.items()
              if v.get("status") == "ok" and v.get("confidence") in ("low", "medium")]
    errs = [p for p, v in manifest.items() if v.get("status") == "error"]
    print(f"\nDone. Per-page: {pages_dir}/  Combined: {combined}")
    if review:
        print(f"Needs human review (low/medium confidence): "
              f"{', '.join(sorted(review, key=int))}")
    if errs:
        print(f"Failed pages: {', '.join(sorted(errs, key=int))} -- rerun to retry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
