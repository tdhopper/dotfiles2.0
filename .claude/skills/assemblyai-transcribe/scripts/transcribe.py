#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
# ]
# ///
"""Transcribe audio files with speaker diarization using AssemblyAI API."""

import argparse
import os
import sys
import time
from pathlib import Path

import httpx

BASE_URL = "https://api.assemblyai.com/v2"

SUPPORTED_FORMATS = {".wav", ".mp3", ".aiff", ".aac", ".ogg", ".flac", ".m4a", ".wma", ".webm"}


def get_headers() -> dict:
    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set ASSEMBLYAI_API_KEY environment variable")
    return {"Authorization": api_key, "Content-Type": "application/json"}


def upload_file(file_path: Path, client: httpx.Client) -> str:
    """Upload a local file to AssemblyAI and return the upload URL."""
    headers = {"Authorization": os.environ["ASSEMBLYAI_API_KEY"]}
    print(f"Uploading {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.1f} MB)...", file=sys.stderr)

    with open(file_path, "rb") as f:
        response = client.post(f"{BASE_URL}/upload", headers=headers, content=f)
    response.raise_for_status()
    return response.json()["upload_url"]


def submit_transcript(
    audio_url: str,
    client: httpx.Client,
    speaker_labels: bool = True,
    speakers_expected: int | None = None,
) -> str:
    """Submit a transcription job and return the transcript ID."""
    payload: dict = {
        "audio_url": audio_url,
        "speaker_labels": speaker_labels,
    }
    if speakers_expected is not None:
        payload["speakers_expected"] = speakers_expected

    response = client.post(f"{BASE_URL}/transcript", headers=get_headers(), json=payload)
    response.raise_for_status()
    data = response.json()
    return data["id"]


def poll_transcript(transcript_id: str, client: httpx.Client) -> dict:
    """Poll until the transcript is ready, return the full response."""
    url = f"{BASE_URL}/transcript/{transcript_id}"
    headers = get_headers()

    while True:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        status = data["status"]

        if status == "completed":
            return data
        elif status == "error":
            raise RuntimeError(f"Transcription failed: {data.get('error', 'unknown error')}")
        else:
            print(f"Status: {status}...", file=sys.stderr)
            time.sleep(5)


def format_timestamp(ms: int) -> str:
    """Convert milliseconds to HH:MM:SS or MM:SS."""
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def format_output(data: dict, fmt: str) -> str:
    """Format transcript data into the requested output format."""
    if fmt == "text":
        return data.get("text", "")

    utterances = data.get("utterances", [])
    if not utterances:
        return data.get("text", "")

    if fmt == "diarized":
        lines = []
        for u in utterances:
            ts = format_timestamp(u["start"])
            lines.append(f"[{ts}] Speaker {u['speaker']}: {u['text']}")
        return "\n\n".join(lines)

    if fmt == "srt":
        lines = []
        for i, u in enumerate(utterances, 1):
            start = format_srt_time(u["start"])
            end = format_srt_time(u["end"])
            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(f"Speaker {u['speaker']}: {u['text']}")
            lines.append("")
        return "\n".join(lines)

    return data.get("text", "")


def format_srt_time(ms: int) -> str:
    """Convert milliseconds to SRT timestamp format HH:MM:SS,mmm."""
    hours = ms // 3_600_000
    ms %= 3_600_000
    minutes = ms // 60_000
    ms %= 60_000
    seconds = ms // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with speaker diarization via AssemblyAI")
    parser.add_argument("audio", help="Local file path or URL to audio")
    parser.add_argument("-o", "--output", type=Path, help="Output file (default: stdout)")
    parser.add_argument(
        "-f", "--format",
        choices=["diarized", "text", "srt"],
        default="diarized",
        help="Output format (default: diarized)",
    )
    parser.add_argument("--no-diarize", action="store_true", help="Disable speaker diarization")
    parser.add_argument("-n", "--speakers", type=int, help="Expected number of speakers")

    args = parser.parse_args()

    audio_input = args.audio
    is_url = audio_input.startswith("http://") or audio_input.startswith("https://")

    if not is_url:
        file_path = Path(audio_input)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        if file_path.suffix.lower() not in SUPPORTED_FORMATS:
            print(f"Error: Unsupported format: {file_path.suffix}. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}", file=sys.stderr)
            sys.exit(1)

    with httpx.Client(timeout=300) as client:
        if is_url:
            audio_url = audio_input
        else:
            audio_url = upload_file(file_path, client)

        print("Submitting transcription job...", file=sys.stderr)
        transcript_id = submit_transcript(
            audio_url,
            client,
            speaker_labels=not args.no_diarize,
            speakers_expected=args.speakers,
        )
        print(f"Transcript ID: {transcript_id}", file=sys.stderr)

        data = poll_transcript(transcript_id, client)
        result = format_output(data, args.format)

        if args.output:
            args.output.write_text(result)
            print(f"Saved to {args.output}", file=sys.stderr)
        else:
            print(result)


if __name__ == "__main__":
    main()
