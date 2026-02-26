#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using Nano Banana 2 (Gemini 3.1 Flash Image) via Spotify's AI Gateway.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--resolution 0.5K|1K|2K|4K] [--api-key KEY] [--compress] [--max-size MB]
"""

import argparse
import base64
import os
import shutil
import subprocess
import sys
from io import BytesIO
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("SPOTIFY_AI_GATEWAY_KEY")


def save_image(image, output_path: Path) -> None:
    """Save PIL image to path, handling mode conversion."""
    from PIL import Image as PILImage

    # Ensure RGB mode for PNG (convert RGBA to RGB with white background if needed)
    if image.mode == 'RGBA':
        rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        rgb_image.save(str(output_path), 'PNG')
    elif image.mode == 'RGB':
        image.save(str(output_path), 'PNG')
    else:
        image.convert('RGB').save(str(output_path), 'PNG')


def compress_png(filepath: Path, max_size_mb: float = 8.0, quality_min: int = 65, quality_max: int = 95) -> bool:
    """Compress PNG using pngquant if available and file exceeds max size.

    Returns True if compression was applied, False otherwise.
    """
    # Check if pngquant is available
    if not shutil.which("pngquant"):
        print("Note: pngquant not installed, skipping compression (install with: brew install pngquant)")
        return False

    # Check current file size
    current_size_mb = filepath.stat().st_size / (1024 * 1024)
    if current_size_mb <= max_size_mb:
        print(f"Image size ({current_size_mb:.1f}MB) already under {max_size_mb}MB, skipping compression")
        return False

    print(f"Compressing {current_size_mb:.1f}MB image (target: <{max_size_mb}MB)...")

    try:
        result = subprocess.run(
            [
                "pngquant",
                f"--quality={quality_min}-{quality_max}",
                "--force",
                "--output", str(filepath),
                str(filepath)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            new_size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"Compressed: {current_size_mb:.1f}MB -> {new_size_mb:.1f}MB")
            return True
        else:
            print(f"Compression warning: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Compression error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana 2 (Gemini 3.1 Flash Image)"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--input-image", "-i",
        help="Optional input image path for editing/modification"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["0.5K", "1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 0.5K, 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Spotify AI Gateway API key (overrides SPOTIFY_AI_GATEWAY_KEY env var)"
    )
    parser.add_argument(
        "--compress", "-c",
        action="store_true",
        default=True,
        help="Compress PNG if over max size (default: enabled)"
    )
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Disable PNG compression"
    )
    parser.add_argument(
        "--max-size", "-m",
        type=float,
        default=8.0,
        help="Max file size in MB before compression (default: 8.0)"
    )

    args = parser.parse_args()

    # Handle --no-compress flag
    if args.no_compress:
        args.compress = False

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set SPOTIFY_AI_GATEWAY_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Import here after checking API key to avoid slow import on error
    from openai import OpenAI
    from PIL import Image as PILImage

    # Initialize client with Spotify AI Gateway
    client = OpenAI(
        api_key=api_key,
        base_url="https://hendrix-genai.spotify.net/taskforce/google/v1",
        default_headers={"apikey": api_key}
    )

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input image if provided
    input_image = None
    output_resolution = args.resolution
    if args.input_image:
        try:
            input_image = PILImage.open(args.input_image)
            print(f"Loaded input image: {args.input_image}")

            # Auto-detect resolution if not explicitly set by user
            if args.resolution == "1K":  # Default value
                # Map input image size to resolution
                width, height = input_image.size
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                else:
                    output_resolution = "1K"
                print(f"Auto-detected resolution: {output_resolution} (from input {width}x{height})")
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            sys.exit(1)

    # Build messages for the API call
    messages = []

    if input_image:
        # Convert input image to base64 for editing
        buffered = BytesIO()
        input_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                },
                {"type": "text", "text": args.prompt}
            ]
        })
        print(f"Editing image with resolution {output_resolution}...")
    else:
        messages.append({
            "role": "user",
            "content": args.prompt
        })
        print(f"Generating image with resolution {output_resolution}...")

    try:
        response = client.chat.completions.create(
            model="gemini-3.1-flash-image-preview",
            messages=messages,
            extra_body={
                "response_modalities": ["TEXT", "IMAGE"],
                "image_config": {"image_size": output_resolution}
            }
        )

        # Process response and extract image
        image_saved = False
        import re

        for choice in response.choices:
            message = choice.message

            if message.content:
                # Parse the content - it contains both text and inline image data
                # Format: "text response\n[inlineData]: data:image/png;base64,<base64_data>"
                content = message.content

                # Extract text before [inlineData]
                if "[inlineData]:" in content:
                    text_part = content.split("[inlineData]:")[0].strip()
                    if text_part:
                        print(f"Model response: {text_part}")

                    # Extract base64 image data
                    match = re.search(r'\[inlineData\]:\s*data:image/[^;]+;base64,(.+)', content, re.DOTALL)
                    if match:
                        b64_data = match.group(1).strip()
                        image_bytes = base64.b64decode(b64_data)
                        image = PILImage.open(BytesIO(image_bytes))
                        save_image(image, output_path)
                        image_saved = True
                else:
                    # No image in response, just text
                    print(f"Model response: {content}")

        if image_saved:
            full_path = output_path.resolve()
            print(f"\nImage saved: {full_path}")

            # Compress if enabled
            if args.compress:
                compress_png(output_path, max_size_mb=args.max_size)
        else:
            print("Error: No image was generated in the response.", file=sys.stderr)
            print(f"Response: {response}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
