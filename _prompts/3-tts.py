#!/usr/bin/env python3
"""
Command-line utility that turns text into speech by calling an OpenAI-compatible
Text-to-Speech (TTS) endpoint over HTTPS.

Differences from 2-tts.py
-------------------------
• Removed the `litellm` dependency – no SDKs are used.
• Performs a direct HTTPS POST request using the `requests` library.
• Still honors the environment variable `OPENAI_API_KEY` for authentication.
• The base URL can be overridden via the environment variable
  `OPENAI_BASE_URL`; otherwise it defaults to the official endpoint
  https://api.openai.com/v1 .

Prerequisites
-------------
pip install --upgrade requests
export OPENAI_API_KEY="sk-..."

Usage
-----
$ python 3-tts.py "Hello world"                # writes speech.wav
$ python 3-tts.py "Hello world" -o hello.wav   # custom output file
$ python 3-tts.py "Hello world" --format mp3   # choose audio format
"""

import argparse
import os
import sys
from typing import Optional

import requests

# Default OpenAI-compatible base URL (can be overridden with env var).
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate speech from text via an OpenAI-compatible TTS endpoint."
    )
    parser.add_argument(
        "text",
        help="Text prompt to synthesize into speech."
    )
    parser.add_argument(
        "-o", "--output",
        default="speech",
        help="Output file name without extension (default: speech)."
    )
    parser.add_argument(
        "--format",
        default="wav",
        choices=["wav", "mp3", "opus", "flac"],
        help="Audio format to request from the API (default: wav)."
    )
    return parser.parse_args()


def request_tts(
    api_key: str,
    text: str,
    audio_format: str,
    base_url: str = DEFAULT_OPENAI_BASE_URL,
    model: str = "gpt-4o-mini-tts",
    voice: str = "alloy",
    instructions: Optional[str] = "Speak in a cheerful and positive tone.",
) -> bytes:
    """
    Send a TTS request and return the binary audio data.

    Raises
    ------
    RuntimeError
        If the HTTP request fails or the response code is not 200.
    """
    url = f"{base_url.rstrip('/')}/audio/speech"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "instructions": instructions,
        "response_format": audio_format,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
    except requests.RequestException as exc:
        raise RuntimeError(f"Network error while contacting {url}: {exc}") from exc

    if response.status_code != 200:
        # Attempt to extract error message from JSON payload.
        message = ""
        try:
            message = response.json().get("error", {}).get("message", "")
        except Exception:
            pass
        raise RuntimeError(
            f"API error {response.status_code}: {message or response.text}"
        )

    return response.content


def main() -> None:
    args = parse_args()

    # Validate environment setup.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.stderr.write("Error: OPENAI_API_KEY environment variable is not set.\n")
        sys.exit(1)

    base_url = os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL)

    try:
        audio_data = request_tts(
            api_key=api_key,
            text=args.text,
            audio_format=args.format,
            base_url=base_url,
        )
    except RuntimeError as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(1)

    # Ensure output file has proper extension.
    output_file = args.output
    if not output_file.lower().endswith(f".{args.format}"):
        output_file = f"{output_file}.{args.format}"

    # Write the audio data to disk.
    try:
        with open(output_file, "wb") as f:
            f.write(audio_data)
    except OSError as exc:
        sys.stderr.write(f"Error writing {output_file}: {exc}\n")
        sys.exit(1)

    print(f"✔ Audio saved to {output_file}")


if __name__ == "__main__":
    main()
