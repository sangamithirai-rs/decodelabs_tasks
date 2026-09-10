"""
ai_engine.py
------------
GENERATIVE AI stage: RAW CODE STRING -> GENERATIVE AI -> STRUCTURED AI RESPONSE

Only this module talks to the Gemini API. It knows nothing about file
paths or terminal rendering.
"""

from __future__ import annotations

import os

from exceptions import AIResponseError

DEFAULT_MODEL = os.environ.get("REVIEWER_MODEL", "gemini-3.6-flash")

SYSTEM_INSTRUCTION = """\
You are a Senior Code Quality Assurance Engineer performing an automated
static code review. You are NOT a conversational assistant.

STRICT BEHAVIOR RULES:
- Do not greet the user. Do not say "Sure", "Here is", "I hope this helps",
  or any conversational filler, before, between, or after your analysis.
- Do not ask questions. Do not offer opinions unrelated to the code.
- Be cold, precise, and analytical. Write like an engineering report, not
  a conversation.
- Only report issues that are actually present in the code. Do NOT invent
  or fabricate problems to appear thorough. If the code has no meaningful
  issues, explicitly state that in the BUG_REPORT section instead of
  inventing minor nitpicks.
- Consider these categories when analyzing: syntax errors, logical errors,
  security/vulnerability issues, and performance issues. Only mention
  categories that are actually relevant to the supplied code.

OUTPUT FORMAT (MANDATORY, FOLLOW EXACTLY):
Your entire response MUST contain exactly these two section headers, in
this exact order, with no extra headers before, between, or after them:

## BUG_REPORT
- Concise bullet point per issue found (or a single bullet stating that
  no meaningful issues were found).

## REFACTORED_CODE
A single Markdown-fenced code block containing the corrected / refactored
version of the entire supplied code. Use the correct language tag on the
fence (e.g. ```python, ```javascript, ```java). Do not include more than
one code block. Do not add explanations inside or around the code block
beyond the code itself.

Do not output anything before "## BUG_REPORT" or after the closing code
fence of "## REFACTORED_CODE". No summaries, no sign-offs.
"""


def _build_user_prompt(code: str, language: str, file_name: str) -> str:
    return (
        f"Review the following {language} source file named '{file_name}'.\n"
        f"Analyze it strictly for syntax errors, logical errors, "
        f"security/vulnerability issues, and performance issues.\n\n"
        f"--- BEGIN SOURCE CODE ---\n"
        f"{code}\n"
        f"--- END SOURCE CODE ---\n"
    )


def analyze_code(code: str, language: str, file_name: str) -> str:
    """Send raw code to the Gemini model and return its raw text reply."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise AIResponseError(
            "GEMINI_API_KEY environment variable is not set. "
            "Set it in your .env file, e.g.:\n"
            "  GEMINI_API_KEY=your-key-here"
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise AIResponseError(
            "The 'google-genai' package is not installed. Run:\n"
            "  pip install -r requirements.txt"
        ) from exc

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=_build_user_prompt(code, language, file_name),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
    except Exception as exc:  # noqa: BLE001 - final safety net around SDK call
        raise AIResponseError(f"Unexpected error calling the AI model: {exc}") from exc

    full_text = (getattr(response, "text", "") or "").strip()

    if not full_text:
        raise AIResponseError("The AI model returned an empty response.")

    return full_text