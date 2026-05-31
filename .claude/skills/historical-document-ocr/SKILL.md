---
name: historical-document-ocr
description: >-
  Transcribe scanned/photographed historical documents (PDFs or images) to text
  with Gemini vision, using accuracy-first practices: per-page high-res
  rendering, faded-scan image enhancement, strict verbatim prompting, and an
  optional multi-model consensus pass that reconciles disagreements by re-reading
  the page. Use this whenever the user wants to OCR, transcribe, or extract the
  text of scanned letters, manuscripts, typescripts, carbon copies, ledgers,
  archival records, genealogy documents, old correspondence, or any image-only
  PDF that has no real text layer — especially when the material is handwritten,
  typewritten, faded, rotated, or hard to read and accuracy matters. Trigger even
  if the user just says "read this old scan", "what does this letter say",
  "digitize these archive pages", or "transcribe this PDF" and the PDF turns out
  to be scanned images. Do NOT use this for audio/podcast transcription (that is
  gemini-podcast-transcribe) or for born-digital PDFs that already contain
  selectable text (a plain pdftotext is enough there).
---

# Historical Document OCR / Transcription

Transcribe scanned historical documents with Gemini, optimized for **accuracy on
degraded material** (faded carbons, handwriting, rotation, low contrast) rather
than speed. The bundled script `scripts/transcribe_documents.py` does the whole
pipeline; this file explains how to drive it well.

## When this is the right tool

This is for **image-only** documents — the pixels *are* the only copy of the
text. If `pdftotext file.pdf -` already returns the real text, the document is
born-digital and you don't need OCR at all. Confirm first:

```bash
pdftotext -f 1 -l 3 INPUT.pdf - | wc -c   # near-zero => scanned images => use this skill
```

## Prerequisites

- `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in the environment.
- `poppler` for `pdftoppm`/`pdftotext` (`brew install poppler`).
- `imagemagick` for faded-scan enhancement (`brew install imagemagick`) —
  optional; the script degrades gracefully without it.
- Python deps (`google-genai`) are installed automatically by `uv run`.

## The core workflow

**1. Look before you transcribe.** Render a few pages and actually read them, so
you know what you're dealing with and can write good context. This one step
drives every later decision (model, enhancement, context).

```bash
pdftoppm -png -r 150 -f 1 -l 4 INPUT.pdf /tmp/peek   # then Read the PNGs
```

Note: handwritten vs typed vs printed? faded? rotated? what's the subject, and
what proper nouns / names / places / dates / era-specific spellings appear? Those
last details become your `--context`.

**2. Write a context block.** Gemini uses it ONLY to disambiguate genuinely
ambiguous characters — it is told never to invent text from it — but it
meaningfully improves accuracy on names, places, and period spellings. Keep it
factual and specific. Example:

```
- Typewritten carbon copies, September 1956.
- Author: Joe B. Hopper, a missionary writing from Chunju, Korea.
- Recipient: Dr. L. Nelson Bell, Montreat, North Carolina.
- The Korean currency "hwan" is spelled "whan" here; keep it as written.
```

**3. Pick the model (accuracy vs cost).** See `references/practices.md` for the
full rationale and current model notes. Short version:
- Default `gemini-3.1-pro-preview` — most faithful on faded/rotated pages and it
  preserves the original's typos instead of silently "correcting" them.
- `gemini-3.5-flash` — near-equal on clean text, cheaper; good at scale.
- `gemini-2.5-flash` — cheapest, but **drops faint lines and scrambles rotated
  text**; avoid on degraded scans.
- At a few-hundred pages the cost gap is pennies, so **buy accuracy** unless the
  job is genuinely large.

Model names change over time. If a call 404s with "no longer available", list
what's live and pick the current successor:

```bash
uv run scripts/transcribe_documents.py --help    # shows defaults
python3 -c "import os;from google import genai;[print(m.name) for m in genai.Client(api_key=os.environ['GEMINI_API_KEY']).models.list() if 'gemini' in m.name]"
```

**4. Smoke-test on the hardest pages first.** Find the most degraded page from
step 1 and run just that, so you catch problems before paying for all 200 pages.

```bash
uv run scripts/transcribe_documents.py INPUT.pdf --pages 5,7-9 \
  --context-file /tmp/context.txt --keep-images
```

**5. Run the full document.** For accuracy-critical work, use `--consensus`
(below). Otherwise a single-model pass is fine.

```bash
uv run scripts/transcribe_documents.py INPUT.pdf --context-file /tmp/context.txt --consensus
```

**6. Report results and the review list.** Tell the user the unanimous/reconciled
split (consensus mode) and which pages have the most disagreements or lowest
confidence — those are the targeted human-review list. Each page's front-matter
holds its `disagreements:` and `notes:`.

## Consensus mode — the accuracy multiplier

`--consensus` transcribes each page with **two independent models**, then:
- if they **agree**, accepts it (tagged `unanimous`, no extra cost);
- if they **disagree**, sends the page image *plus* both candidate transcriptions
  to a judge model that **re-reads the pixels** to adjudicate, marking truly
  ambiguous spots `[illegible]` instead of guessing.

Independent models make independent errors, so agreement is a strong correctness
signal and disagreements pinpoint exactly where to look. Cost is ~2–3× a single
pass. Tune voters with `--voters "modelA,modelB,modelA:0.4"` (a `:TEMP` suffix
adds a temperature-jittered voter) and the adjudicator with `--judge-model`.

## Output layout

Writes to `transcriptions/<pdf-stem>/` (override with `-o`):
- `pages/page-NNN.md` — one page each, with YAML front-matter:
  `confidence`, `illegible_count`, `rotation_observed`, `notes`, and (consensus
  mode) `consensus:` + a `disagreements:` list of the exact words the models
  split on.
- `_combined.md` — the full document, page-delimited.
- `manifest.json` — machine-readable per-page status (drives review triage).
- `images/` — rendered PNGs, only with `--keep-images` (these get large at
  300 DPI; don't commit them — regenerate when needed).

The run is **resumable and idempotent**: finished pages are skipped unless
`--force`, so a failed/interrupted run just gets re-run. Failed pages are
retried with exponential backoff and listed at the end.

## Key flags

| Flag | Purpose |
|------|---------|
| `--consensus` | multi-model + image-grounded reconciliation (accuracy) |
| `--context` / `--context-file` | disambiguation context (names, dates, spellings) |
| `-m MODEL` | single-pass model (default `gemini-3.1-pro-preview`) |
| `--voters` / `--judge-model` | configure consensus models |
| `--pages 5,7-9` | transcribe a subset (smoke tests, re-runs) |
| `--no-enhance` | skip ImageMagick contrast/deskew (use on clean scans) |
| `--force` | re-transcribe pages that already exist |
| `--keep-images` | keep rendered PNGs for visual review |
| `--dpi` `--max-tokens` | render resolution / output cap (defaults 300 / 32768) |

## Quality expectations & verification

Even at state of the art, expect ~1–4% word error on faded/handwritten material;
the failure modes are **skipped lines** and **word substitutions**, not
fabrication (the prompt forbids inventing text). For archival-grade output,
always do a human pass on the flagged disagreement spans against the page images
— consensus mode is what makes that pass small and targeted. See
`references/practices.md` for the research these defaults are based on, the model
selection evidence, and troubleshooting.
