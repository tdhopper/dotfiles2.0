# Practices, model evidence, and troubleshooting

Background for `historical-document-ocr`. Read this when choosing a model,
explaining the approach, or debugging poor output.

## Why these defaults (the research)

Recent work shows frontier vision models now beat specialized HTR systems on
historical handwriting. Gemini 3-class models reached ~1.67% character error
rate / ~4.42% word error rate in strict testing — roughly half the error of
Transkribus, the best-known dedicated HTR tool — with **no hallucination** when
prompted for verbatim output (~20 errors across 100k words). The bundled script
encodes the settings those results came from:

- **Temperature 0** — deterministic, consistent reads.
- **High media resolution** — more visual detail per page.
- **Minimal thinking budget** — counterintuitively, *more* reasoning tends to
  *degrade* visual OCR; the model should read, not ruminate.
- **Large `max_output_tokens` (32768)** — the API default (~8192) silently
  truncates dense pages mid-transcription. This is a common, invisible failure;
  keep the cap high.
- **One page per API call at 300 DPI** — maximizes resolution per image, avoids
  whole-PDF truncation, and makes each page independently retryable/resumable.
- **Strict verbatim prompt** — preserve original spelling, typos, punctuation,
  capitalization, and line breaks; mark unreadable spans `[illegible]`; never
  invent text; tag `[handwritten:]` / `[margin:]`.
- **Document context injected** — a known accuracy lever for proper nouns and
  period spellings; the prompt restricts it to disambiguation only.
- **Faded-carbon preprocessing** (ImageMagick: grayscale → deskew →
  contrast-stretch → normalize) — the single biggest win on low-contrast scans.

Sources worth re-reading if revisiting this skill:
- generativehistory.substack.com — "Gemini 3 Solves Handwriting Recognition"
  (settings, CER/WER numbers, failure modes).
- github.com/asreynolds1000/gemini-vision-ocr-guide (OCR prompt patterns,
  the truncation/token caveat).
- ai.google.dev/gemini-api/docs/pricing (current per-token prices; image/PDF
  tokens are billed at the image rate).

## Model selection — measured, not assumed

Benchmarked head-to-head on a real 1956 typed-and-faded carbon corpus (dense
pages, many rotated 90°):

| Model | Behavior on degraded pages |
|-------|----------------------------|
| `gemini-3.1-pro-preview` | Most complete and faithful; **preserves the typist's original errors** (e.g. kept `insistance`, kept period currency `whan`). Best default. |
| `gemini-3.5-flash` | ~99% identical on clean text; cheaper. But silently *normalizes* — "corrected" `insistance`→`insistence`, `whan`→`won` — which is wrong for verbatim archival work. Made a couple OCR errors on the faintest lines. |
| `gemini-2.5-flash` | Disqualified for degraded scans: dropped ~17% of text on a dense page and scrambled the structure of rotated text. Fine only for clean, high-contrast pages. |

Takeaways:
- For **faded/handwritten/rotated** material, prefer a **Pro-tier** model.
- The accuracy/cost tradeoff only bites at large scale. At tens-to-hundreds of
  pages the cost difference is pennies — **buy accuracy**.
- At thousands of pages, use `gemini-3.5-flash` as voters and escalate only the
  disagreements to a Pro judge (which is exactly what `--consensus` does).

**Model names drift.** Preview models get deprecated (e.g. `gemini-3-pro-preview`
became a 404). If a call fails with "no longer available", list live models
(command in SKILL.md) and substitute the current successor via `-m`,
`--voters`, and `--judge-model`.

## Why consensus works

Two *independent* models fail in *different* places, so:
- agreement across models is strong evidence the read is correct;
- disagreement localizes the few spots that need scrutiny;
- re-feeding the image + both candidates to a judge resolves those spots by
  **evidence (the pixels)**, not by majority vote — and lets it honestly fall
  back to `[illegible]` when the image truly doesn't support either reading.

This converts "re-read all N pages" into "check the handful of flagged words",
which is the difference between a feasible and an infeasible human QA pass.

## Troubleshooting

- **Transcription cut off / ends mid-sentence** → output token cap; raise
  `--max-tokens`. (Already 32768 by default; very dense pages may need more.)
- **Model "fixed" a historical spelling** → it normalized to modern usage. Use a
  Pro voter and add the era-specific term to `--context` ("the currency is spelled
  'whan', keep as written"). Consensus + Pro judge usually preserves it.
- **Garbled / scrambled rotated text** → you're likely on `gemini-2.5-flash`;
  move to a Pro/3.x model. The models read rotated text fine; the cheap tier
  mis-segments it.
- **Faint page returns mostly `[illegible]`** → ensure ImageMagick is installed
  (enhancement runs automatically). Try a higher `--dpi` (e.g. 400). If a scan is
  genuinely blank/ghosted, `[no legible text]` is the correct, honest output.
- **`pdftoppm: command not found`** → `brew install poppler`.
- **Everything 404s** → deprecated model name; list live models and update flags.
- **Costs higher than expected** → consensus runs 2 passes everywhere plus a
  judge pass on every disagreement. On clean documents most pages are unanimous
  (no judge call); on heavily degraded ones nearly every page reconciles. Drop to
  a single-model pass if accuracy headroom isn't needed.

## Adapting the prompt

The verbatim prompt and metadata schema live near the top of
`scripts/transcribe_documents.py` (`PROMPT_TEMPLATE`, `RECONCILE_PROMPT`). Edit
there if a corpus needs different conventions (e.g. different marginalia tags,
or to emit TEI/structured output instead of plain text). Keep the trailing
single-line JSON metadata contract intact — the script parses it for the
manifest and the review triage.
