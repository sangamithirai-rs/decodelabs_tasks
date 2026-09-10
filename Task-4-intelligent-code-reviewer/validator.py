"""
validator.py
------------
RESPONSE VALIDATION stage:
STRUCTURED AI RESPONSE -> RESPONSE VALIDATION -> MARKDOWN RENDERING

Confirms the AI response actually follows the mandatory structure before
it gets handed to the renderer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from exceptions import ResponseValidationError

BUG_REPORT_HEADER = "## BUG_REPORT"
REFACTORED_CODE_HEADER = "## REFACTORED_CODE"

# Matches a Markdown fenced code block: ```optional_lang\n ... \n```
_CODE_FENCE_PATTERN = re.compile(r"```[a-zA-Z0-9_+-]*\n(.*?)```", re.DOTALL)


@dataclass
class ValidatedResponse:
    """A parsed, structurally-verified AI response."""
    bug_report: str
    refactored_code: str
    code_language_tag: str
    raw_response: str


def validate_response(raw_response: str) -> ValidatedResponse:
    """Validate and parse the AI's raw text response.

    Enforces:
      - Both required headers are present, in order.
      - BUG_REPORT section is non-empty.
      - REFACTORED_CODE section contains exactly one fenced code block.
    """
    if not raw_response or not raw_response.strip():
        raise ResponseValidationError("AI response was empty.")

    text = raw_response.strip()

    if BUG_REPORT_HEADER not in text:
        raise ResponseValidationError(
            f"Missing required section header '{BUG_REPORT_HEADER}' in AI response."
        )
    if REFACTORED_CODE_HEADER not in text:
        raise ResponseValidationError(
            f"Missing required section header '{REFACTORED_CODE_HEADER}' in AI response."
        )

    bug_index = text.index(BUG_REPORT_HEADER)
    code_index = text.index(REFACTORED_CODE_HEADER)

    if bug_index > code_index:
        raise ResponseValidationError(
            f"'{BUG_REPORT_HEADER}' must appear before '{REFACTORED_CODE_HEADER}'."
        )

    bug_report_section = text[bug_index + len(BUG_REPORT_HEADER):code_index].strip()
    refactored_section = text[code_index + len(REFACTORED_CODE_HEADER):].strip()

    if not bug_report_section:
        raise ResponseValidationError(f"'{BUG_REPORT_HEADER}' section is empty.")

    code_blocks = _CODE_FENCE_PATTERN.findall(text[code_index:])

    if len(code_blocks) == 0:
        raise ResponseValidationError(
            f"No Markdown-fenced code block found under '{REFACTORED_CODE_HEADER}'."
        )
    if len(code_blocks) > 1:
        raise ResponseValidationError(
            f"Expected exactly ONE fenced code block under "
            f"'{REFACTORED_CODE_HEADER}', found {len(code_blocks)}."
        )

    refactored_code = code_blocks[0].strip()
    if not refactored_code:
        raise ResponseValidationError("Refactored code block is empty.")

    fence_match = re.search(r"```([a-zA-Z0-9_+-]*)\n", text[code_index:])
    language_tag = fence_match.group(1) if fence_match else ""

    return ValidatedResponse(
        bug_report=bug_report_section,
        refactored_code=refactored_code,
        code_language_tag=language_tag,
        raw_response=text,
    )