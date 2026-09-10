"""
main.py
-------
Entry point. Wires together the full pipeline:

    CODE FILE
      -> FILE INGESTION        (file_handler.py)
      -> RAW CODE STRING
      -> GENERATIVE AI         (ai_engine.py)
      -> STRUCTURED AI RESPONSE
      -> RESPONSE VALIDATION   (validator.py)
      -> MARKDOWN RENDERING    (renderer.py)
      -> TERMINAL OUTPUT

Usage:
    python main.py path/to/file.py
    python main.py                      (will prompt for a path)
"""

from __future__ import annotations

import sys

from exceptions import (
    AIResponseError,
    CodeReviewerError,
    FileIngestionError,
    ResponseValidationError,
    UnsupportedFileTypeError,
)
from file_handler import get_language_from_extension, read_code_file
from ai_engine import analyze_code
from validator import validate_response
from renderer import render_response

# Optional convenience: load ANTHROPIC_API_KEY from a local .env file if
# python-dotenv is installed. Not required, but makes local dev easier.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_file_path_from_args_or_prompt() -> str:
    """Return the target file path from CLI args, or prompt interactively."""
    if len(sys.argv) > 1:
        return sys.argv[1].strip()

    try:
        path = input("Enter path to a .py, .js, or .java file to review: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nNo input received. Exiting.")
        sys.exit(1)

    if not path:
        print("No file path provided. Exiting.")
        sys.exit(1)
    return path


def main() -> None:
    file_path = get_file_path_from_args_or_prompt()

    # --- 1. FILE INGESTION -> RAW CODE STRING ---
    try:
        language = get_language_from_extension(file_path)
        raw_code = read_code_file(file_path)
    except UnsupportedFileTypeError as exc:
        print(f"[Unsupported File Type] {exc}")
        sys.exit(1)
    except FileIngestionError as exc:
        print(f"[File Error] {exc}")
        sys.exit(1)

    print(f"Loaded '{file_path}' ({language}, {len(raw_code)} characters). "
          f"Sending to AI for review...\n")

    # --- 2. GENERATIVE AI -> STRUCTURED AI RESPONSE ---
    try:
        raw_response = analyze_code(raw_code, language, file_path)
    except AIResponseError as exc:
        print(f"[AI Error] {exc}")
        sys.exit(1)

    # --- 3. RESPONSE VALIDATION ---
    try:
        validated = validate_response(raw_response)
    except ResponseValidationError as exc:
        print(f"[Validation Error] AI response did not match the required format: {exc}")
        print("\n--- RAW AI RESPONSE (for debugging) ---\n")
        print(raw_response)
        sys.exit(1)

    # --- 4. MARKDOWN RENDERING -> TERMINAL OUTPUT ---
    render_response(validated, file_path)


if __name__ == "__main__":
    try:
        main()
    except CodeReviewerError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)