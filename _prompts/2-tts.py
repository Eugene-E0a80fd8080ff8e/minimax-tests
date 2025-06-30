#!/usr/bin/env python3
"""
Command-line utility that turns text into speech using an OpenAI-compatible
endpoint via LiteLLM.

Prerequisites
-------------
• The `litellm` Python package must be installed:
      pip install --upgrade litellm
• The environment variable `OPENAI_API_KEY` must contain a valid key.

Usage
-----
$ python 2-tts.py "Hello world"                # writes speech.wav
$ python 2-tts.py "Hello world" -o hello.wav   # custom output file
$ python 2-tts.py "Hello world" --format mp3   # choose audio format
"""

import argparse
import os
import sys
from litellm import OpenAI

# Explicitly set the OpenAI-compatible base URL.
OPENAI_BASE_URL = "https://api.openai.com/v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate speech from text using an OpenAI-compatible TTS endpoint."
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


def main() -> None:
    args = parse_args()

    # Ensure the API key is available.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.stderr.write("Error: OPENAI_API_KEY environment variable is not set.\n")
        sys.exit(1)

    # Create a LiteLLM (OpenAI-compatible) client.
    client = OpenAI(
        api_key=api_key,
        base_url=OPENAI_BASE_URL
    )

    # Call the TTS endpoint.
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=args.text,
        instructions="Speak in a cheerful and positive tone.",
        response_format=args.format
    )

    # Retrieve binary audio.
    audio_data = getattr(response, "audio", None)
    if audio_data is None:
        # Fallbacks for different SDK versions.
        if hasattr(response, "content"):
            audio_data = response.content
        elif hasattr(response, "read"):
            audio_data = response.read()

    if audio_data is None:
        sys.stderr.write("Error: Could not extract audio data from response.\n")
        sys.exit(1)

    # Ensure the output file has the correct extension.
    output_file = args.output
    if not output_file.lower().endswith(f".{args.format}"):
        output_file = f"{output_file}.{args.format}"

    # Write audio to disk.
    with open(output_file, "wb") as f:
        f.write(audio_data)

    print(f"✔ Audio saved to {output_file}")


if __name__ == "__main__":
    main()
