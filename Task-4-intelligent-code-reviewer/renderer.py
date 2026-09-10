"""
renderer.py
-----------
MARKDOWN RENDERING -> TERMINAL OUTPUT stage.

Takes a validated response and prints it to the terminal as formatted
Markdown using 'rich'. Falls back to plain text if 'rich' isn't installed.
"""

from __future__ import annotations

from validator import ValidatedResponse


def render_response(validated: ValidatedResponse, file_name: str) -> None:
    """Render a validated AI response to the terminal as Markdown."""
    try:
        _render_with_rich(validated, file_name)
    except ImportError:
        _render_plain(validated, file_name)


def _render_with_rich(validated: ValidatedResponse, file_name: str) -> None:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel

    console = Console()

    console.print(
        Panel(
            f"[bold]Intelligent Code Reviewer & Explainer[/bold]\n"
            f"File analyzed: [cyan]{file_name}[/cyan]",
            style="bold blue",
        )
    )

    markdown_text = (
        f"## BUG_REPORT\n\n{validated.bug_report}\n\n"
        f"## REFACTORED_CODE\n\n"
        f"```{validated.code_language_tag}\n{validated.refactored_code}\n```\n"
    )

    console.print(Markdown(markdown_text))


def _render_plain(validated: ValidatedResponse, file_name: str) -> None:
    print("=" * 70)
    print("Intelligent Code Reviewer & Explainer")
    print(f"File analyzed: {file_name}")
    print("=" * 70)
    print()
    print("## BUG_REPORT")
    print()
    print(validated.bug_report)
    print()
    print("## REFACTORED_CODE")
    print()
    print(f"```{validated.code_language_tag}")
    print(validated.refactored_code)
    print("```")