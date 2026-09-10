"""
file_handler.py
----------------
FILE INGESTION stage: CODE FILE -> FILE INGESTION -> RAW CODE STRING
"""

from __future__ import annotations

import os

from exceptions import FileIngestionError, UnsupportedFileTypeError

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
}

MAX_FILE_SIZE_BYTES = 2_000_000  # ~2 MB


def get_language_from_extension(file_path: str) -> str:
    """Return the language name for a file's extension, or raise if unsupported."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise UnsupportedFileTypeError(
            f"Unsupported file extension '{ext or '(none)'}'. "
            f"Supported extensions are: {supported}"
        )
    return SUPPORTED_EXTENSIONS[ext]


def read_code_file(file_path: str) -> str:
    """Read a source code file and return its full contents as a string."""
    # 1. Validate extension before touching the filesystem.
    get_language_from_extension(file_path)

    # 2. Existence checks.
    if not os.path.exists(file_path):
        raise FileIngestionError(f"File not found: '{file_path}'")
    if not os.path.isfile(file_path):
        raise FileIngestionError(f"Path is not a file: '{file_path}'")

    # 3. Size guard.
    try:
        size = os.path.getsize(file_path)
    except OSError as exc:
        raise FileIngestionError(f"Could not read file size for '{file_path}': {exc}")

    if size == 0:
        raise FileIngestionError(f"File '{file_path}' is empty. Nothing to review.")
    if size > MAX_FILE_SIZE_BYTES:
        raise FileIngestionError(
            f"File '{file_path}' is too large ({size:,} bytes). "
            f"Limit is {MAX_FILE_SIZE_BYTES:,} bytes."
        )

    # 4. Actual read, with each failure mode mapped explicitly.
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contents = f.read()
    except FileNotFoundError as exc:
        raise FileIngestionError(f"File not found: '{file_path}'") from exc
    except PermissionError as exc:
        raise FileIngestionError(
            f"Permission denied when trying to read '{file_path}'."
        ) from exc
    except UnicodeDecodeError as exc:
        raise FileIngestionError(
            f"'{file_path}' is not valid UTF-8 text and could not be decoded. ({exc})"
        ) from exc
    except OSError as exc:
        raise FileIngestionError(f"Could not read '{file_path}': {exc}") from exc

    if not contents.strip():
        raise FileIngestionError(f"File '{file_path}' contains no code to review.")

    return contents