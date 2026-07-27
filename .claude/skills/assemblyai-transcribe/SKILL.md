---
name: assemblyai-transcribe
description: |
  Transcribe podcast and audio files with speaker diarization using AssemblyAI API. Use when the user wants to:
  (1) Transcribe a podcast or audio file with AssemblyAI,
  (2) Get speaker-labeled transcripts (who said what),
  (3) Diarize audio to identify different speakers,
  (4) Generate SRT subtitles from audio.
  Triggers on: "assemblyai", "transcribe with assemblyai", "diarize podcast", "assemblyai transcribe".
---

# Podcast Transcription with AssemblyAI

Transcribe audio files with speaker diarization using `scripts/transcribe.py`.

## Requirements

- Set `ASSEMBLYAI_API_KEY` environment variable
- Dependencies installed automatically via `uv run`

## Supported Formats

WAV, MP3, AIFF, AAC, OGG, FLAC, M4A, WMA, WEBM

## Usage

Transcribe a local file with speaker diarization (default):
```bash
uv run scripts/transcribe.py /path/to/podcast.mp3
```

Transcribe from a URL:
```bash
uv run scripts/transcribe.py https://example.com/podcast.mp3
```

Save to file:
```bash
uv run scripts/transcribe.py /path/to/podcast.mp3 -o transcript.txt
```

Specify expected number of speakers:
```bash
uv run scripts/transcribe.py /path/to/podcast.mp3 -n 3
```

Plain text output (no speaker labels):
```bash
uv run scripts/transcribe.py /path/to/podcast.mp3 --no-diarize -f text
```

SRT subtitle format:
```bash
uv run scripts/transcribe.py /path/to/podcast.mp3 -f srt -o subtitles.srt
```

## Options

| Flag | Description |
|------|-------------|
| `-o, --output` | Output file path (default: stdout) |
| `-f, --format` | Output format: `diarized` (default), `text`, `srt` |
| `--no-diarize` | Disable speaker diarization |
| `-n, --speakers` | Expected number of speakers (helps accuracy) |

## Output Formats

- **diarized** (default): `[MM:SS] Speaker A: text` with blank lines between utterances
- **text**: Plain transcript without speaker labels or timestamps
- **srt**: SRT subtitle format with speaker labels

## Notes

- Local files are uploaded to AssemblyAI's servers for processing, then transcribed
- URLs are passed directly (the audio must be publicly accessible)
- Polling interval is 5 seconds; long audio files may take several minutes
- By default, AssemblyAI detects up to 10 speakers; use `-n` to hint if you know the count
