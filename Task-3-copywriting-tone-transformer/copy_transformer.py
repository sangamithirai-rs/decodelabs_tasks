"""
Automated Copywriting & Tone Transformer
==========================================
Takes a raw product description and generates platform-tailored marketing
copy using the Anthropic API.

MODEL NOTE:
This script targets `claude-sonnet-4-6`, NOT the newer `claude-sonnet-5`
(or Opus 4.7+). As of mid-2026, Anthropic's newest models reject
non-default `temperature` / `top_p` / `top_k` values with a 400 error —
sampling control was replaced by an `effort` parameter and prompt-based
guidance. Since this app is built around tunable inference parameters,
we deliberately pin to a model generation that still honors them.
If you later migrate to Sonnet 5+, strip the sampling params from
`call_claude()` and control variety via the prompt/system message instead.

Install:
    pip install anthropic python-dotenv --break-system-packages

Auth (choose one):
    1) export ANTHROPIC_API_KEY="sk-ant-..."          (shell session only)
    2) Create a .env file next to this script:
           ANTHROPIC_API_KEY=sk-ant-...
       (persists across sessions; loaded automatically via python-dotenv.
       Add .env to your .gitignore — never commit real keys.)

Usage (CLI):
    python copy_transformer.py \
        --product "AquaPure Mini" \
        --description "A compact countertop water filter that removes 99% of contaminants in 60 seconds." \
        --platform linkedin \
        --tone professional

No API key / no billing set up? Add --dry-run to print the compiled prompt
instead of calling the API. Paste the printed prompt into claude.ai (free)
and get the same copy by hand:
    python copy_transformer.py --product "AquaPure Mini" \
        --description "..." --platform instagram --tone playful --dry-run

Usage (as a library):
    from copy_transformer import generate_copy
    text = generate_copy(
        product_name="AquaPure Mini",
        raw_description="A compact countertop water filter...",
        platform="instagram",
        tone="playful",
    )
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from string import Template
from typing import Optional

try:
    import anthropic
except ImportError:
    print("Missing dependency. Run: pip install anthropic --break-system-packages")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads ANTHROPIC_API_KEY (and anything else) from a .env file if present
except ImportError:
    # dotenv is optional — script still works if ANTHROPIC_API_KEY is exported in the shell
    pass


# ---------------------------------------------------------------------------
# 1. Platform configuration
# ---------------------------------------------------------------------------
# Each platform gets its own prompt template, structural guidance, and a
# default (temperature, top_p) pair reflecting how "creative" vs.
# "controlled" that platform's copy typically should be.

@dataclass(frozen=True)
class PlatformConfig:
    name: str
    guidance: str          # style/structure instructions injected into the prompt
    max_tokens: int
    default_temperature: float
    default_top_p: float


PLATFORM_CONFIGS: dict[str, PlatformConfig] = {
    "linkedin": PlatformConfig(
        name="LinkedIn",
        guidance=(
            "Write a LinkedIn post. Open with a hook line that states a problem "
            "or insight. Use short paragraphs (1-2 sentences each) with line "
            "breaks for readability. Include 3-5 relevant hashtags at the end. "
            "Keep it credible and value-oriented, not salesy. Target length: "
            "80-150 words."
        ),
        max_tokens=400,
        default_temperature=0.6,   # more controlled/professional
        default_top_p=0.9,
    ),
    "instagram": PlatformConfig(
        name="Instagram",
        guidance=(
            "Write an Instagram caption. Start with a scroll-stopping first "
            "line. Use an energetic, visual voice, tasteful emojis, and short "
            "punchy lines. End with a call-to-action and 5-8 relevant hashtags. "
            "Target length: 40-100 words."
        ),
        max_tokens=350,
        default_temperature=0.9,   # more expressive/creative
        default_top_p=0.95,
    ),
    "email": PlatformConfig(
        name="Email",
        guidance=(
            "Write a marketing email. Include a subject line (prefixed with "
            "'Subject:'), a short preview line, a greeting, 2-3 short body "
            "paragraphs building interest and value, and a clear single "
            "call-to-action button text at the end (prefixed with 'CTA:'). "
            "Target length: 120-200 words."
        ),
        max_tokens=500,
        default_temperature=0.5,   # most controlled, conversion-focused
        default_top_p=0.85,
    ),
}

TONE_DESCRIPTIONS: dict[str, str] = {
    "professional": "polished, confident, and credible, avoiding slang or hype",
    "playful": "fun, witty, and light-hearted, with room for humor and personality",
    "urgent": "energetic and action-driving, emphasizing scarcity or timeliness",
    "luxury": "elegant, refined, and aspirational, understated rather than loud",
    "friendly": "warm, conversational, and approachable, like talking to a friend",
}


# ---------------------------------------------------------------------------
# 2. Dynamic prompt template
# ---------------------------------------------------------------------------
# string.Template keeps variable injection explicit and avoids accidental
# collisions with literal curly braces if you later add JSON examples etc.

PROMPT_TEMPLATE = Template(
    """You are an expert copywriter specializing in $platform_name marketing content.

PRODUCT: $product_name
RAW DESCRIPTION: $raw_description

TONE: Write in a $tone_description tone.

PLATFORM REQUIREMENTS:
$platform_guidance

Return ONLY the finished copy — no preamble, no explanation, no markdown headers."""
)


def build_prompt(
    product_name: str,
    raw_description: str,
    platform_cfg: PlatformConfig,
    tone: str,
) -> str:
    tone_description = TONE_DESCRIPTIONS.get(tone.lower(), tone)  # fall back to raw tone text
    return PROMPT_TEMPLATE.substitute(
        platform_name=platform_cfg.name,
        product_name=product_name,
        raw_description=raw_description.strip(),
        tone_description=tone_description,
        platform_guidance=platform_cfg.guidance,
    )


# ---------------------------------------------------------------------------
# 3. Inference call with tunable sampling parameters
# ---------------------------------------------------------------------------

def call_claude(
    prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    model: str = "claude-sonnet-4-6",
    client: Optional["anthropic.Anthropic"] = None,
) -> str:
    """
    Sends the compiled prompt to Claude with explicit sampling control.

    temperature: 0.0-1.0. Lower = more deterministic/on-brand, higher = more
                 varied phrasing. Anthropic recommends tuning temperature OR
                 top_p, not both aggressively — here we set both but keep
                 top_p high (>=0.85) so it rarely constrains beyond temperature.
    top_p:       0.0-1.0 nucleus sampling cutoff.
    """
    if not (0.0 <= temperature <= 1.0):
        raise ValueError("temperature must be between 0.0 and 1.0")
    if not (0.0 <= top_p <= 1.0):
        raise ValueError("top_p must be between 0.0 and 1.0")

    client = client or anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        messages=[{"role": "user", "content": prompt}],
    )

    return "".join(block.text for block in response.content if block.type == "text").strip()


# ---------------------------------------------------------------------------
# 4. Public entry point
# ---------------------------------------------------------------------------

def generate_copy(
    product_name: str,
    raw_description: str,
    platform: str,
    tone: str,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    model: str = "claude-sonnet-4-6",
) -> str:
    """
    High-level function: raw description in, platform-tailored copy out.

    temperature / top_p are optional overrides. If omitted, each platform's
    sensible default is used (see PLATFORM_CONFIGS).
    """
    platform_key = platform.strip().lower()
    if platform_key not in PLATFORM_CONFIGS:
        raise ValueError(
            f"Unsupported platform '{platform}'. Choose from: {list(PLATFORM_CONFIGS)}"
        )

    cfg = PLATFORM_CONFIGS[platform_key]
    prompt = build_prompt(product_name, raw_description, cfg, tone)

    return call_claude(
        prompt=prompt,
        max_tokens=cfg.max_tokens,
        temperature=temperature if temperature is not None else cfg.default_temperature,
        top_p=top_p if top_p is not None else cfg.default_top_p,
        model=model,
    )


# ---------------------------------------------------------------------------
# 5. CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate platform-tailored marketing copy.")
    parser.add_argument("--product", required=True, help="Product name")
    parser.add_argument("--description", required=True, help="Raw product description")
    parser.add_argument(
        "--platform", required=True, choices=list(PLATFORM_CONFIGS), help="Target platform"
    )
    parser.add_argument(
        "--tone",
        default="professional",
        help=f"Tone. Presets: {list(TONE_DESCRIPTIONS)} (or any free-text tone)",
    )
    parser.add_argument("--temperature", type=float, default=None, help="Override sampling temperature (0.0-1.0)")
    parser.add_argument("--top-p", type=float, default=None, dest="top_p", help="Override nucleus sampling top_p (0.0-1.0)")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Model ID to call")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip the API call entirely. Just print the compiled prompt so you can "
             "paste it into claude.ai (or anywhere else) by hand. No API key needed.",
    )

    args = parser.parse_args()

    if args.dry_run:
        platform_key = args.platform.strip().lower()
        cfg = PLATFORM_CONFIGS[platform_key]
        prompt = build_prompt(args.product, args.description, cfg, args.tone)

        print("\n" + "=" * 60)
        print(f"DRY RUN — {cfg.name} prompt (tone: {args.tone})")
        print("Paste everything below into claude.ai and send it.")
        print("=" * 60)
        print(prompt)
        print("=" * 60 + "\n")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: set the ANTHROPIC_API_KEY environment variable first "
              "(or use --dry-run to skip the API entirely).")
        sys.exit(1)

    try:
        copy_text = generate_copy(
            product_name=args.product,
            raw_description=args.description,
            platform=args.platform,
            tone=args.tone,
            temperature=args.temperature,
            top_p=args.top_p,
            model=args.model,
        )
    except (ValueError, anthropic.APIError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"{PLATFORM_CONFIGS[args.platform.lower()].name} copy — tone: {args.tone}")
    print("=" * 60)
    print(copy_text)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()