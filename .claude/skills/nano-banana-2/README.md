# Nano Banana 2

A Claude Code skill for generating and editing images using Google's Gemini 3.1 Flash Image model via Spotify's AI Gateway.

## What it does

- **Text-to-image**: Generate images from text prompts
- **Image-to-image**: Edit existing images with natural language instructions
- **Multiple resolutions**: 0.5K, 1K (default), 2K, 4K
- **Auto-compression**: Large PNGs are compressed with pngquant when over 8MB

## Usage

Invoke via Claude Code:

```
/nano-banana-2 a serene Japanese garden with cherry blossoms
```

Or ask naturally — Claude will use this skill when you request image generation or editing.

## How it works

The skill wraps a Python script (`scripts/generate_image.py`) that calls the Gemini 3.1 Flash Image model through Spotify's AI Gateway (`hendrix-genai.spotify.net`). It uses the OpenAI-compatible API format with `response_modalities: ["TEXT", "IMAGE"]`.

### Default workflow

1. **Draft at 1K** — fast iteration to nail the prompt
2. **Iterate** — adjust the prompt in small diffs
3. **Final at 4K** — only when the prompt is locked in

### Editing images

Pass `--input-image` to edit an existing image. The resolution auto-detects from the input dimensions unless explicitly overridden.

## Requirements

- `uv` (for running the script with inline dependencies)
- VPN connected (required for AI Gateway access)
- `SPOTIFY_AI_GATEWAY_KEY` environment variable (or pass `--api-key`)
- `pngquant` (optional, for compression — `brew install pngquant`)

## Files

```
nano-banana-2/
├── SKILL.md                    # Skill definition (instructions for Claude)
├── README.md                   # This file
└── scripts/
    └── generate_image.py       # Image generation/editing script
```
