\# Copywriting \& Tone Transformer



An automated tool that takes a raw product description and generates

professional, platform-tailored marketing copy using Claude (Anthropic API).



\## What it does



Give it a product name, a raw description, a target platform, and a tone —

it compiles a dynamic prompt and returns finished marketing copy ready to

post.



\*\*Supported platforms:\*\* LinkedIn, Instagram, Email

\*\*Supported tones:\*\* professional, playful, urgent, luxury, friendly (or any free-text tone)



\## Key features



\- \*\*Dynamic prompt template compilation\*\* — each platform has its own

&#x20; structural rules (length, format, hashtag/CTA conventions) injected into a

&#x20; reusable `string.Template`.

\- \*\*Inference parameter tuning\*\* — `temperature` and `top\_p` are exposed as

&#x20; CLI flags, with sensible per-platform defaults (e.g. Email is more

&#x20; controlled at `temperature=0.5`, Instagram more expressive at `0.9`).

\- \*\*Dry-run mode\*\* — no API key or billing required. `--dry-run` prints the

&#x20; fully compiled prompt so you can paste it into \[claude.ai](https://claude.ai)

&#x20; by hand and get the same result for free.



\## Setup



```bash

pip install anthropic python-dotenv --break-system-packages

```



\*\*If you have API billing set up:\*\*

Create a `.env` file in this folder:

```

ANTHROPIC\_API\_KEY=sk-ant-your-real-key-here

```



\*\*If you don't:\*\* skip the above — use `--dry-run` instead (see below).



\## Usage



\*\*With API access:\*\*

```bash

python copy\_transformer.py \\

&#x20; --product "AquaPure Mini" \\

&#x20; --description "A compact countertop water filter that removes 99% of contaminants in 60 seconds." \\

&#x20; --platform instagram \\

&#x20; --tone playful

```



\*\*Without API access (dry run):\*\*

```bash

python copy\_transformer.py \\

&#x20; --product "AquaPure Mini" \\

&#x20; --description "A compact countertop water filter that removes 99% of contaminants in 60 seconds." \\

&#x20; --platform instagram \\

&#x20; --tone playful \\

&#x20; --dry-run

```

This prints a ready-to-use prompt — paste it into claude.ai to get the copy.



\### Optional flags



| Flag | Description |

|---|---|

| `--temperature` | Override sampling temperature (0.0–1.0) |

| `--top-p` | Override nucleus sampling top\_p (0.0–1.0) |

| `--model` | Model ID to call (default: `claude-sonnet-4-6`) |



> \*\*Note:\*\* Anthropic's newest models (Claude Sonnet 5, Opus 4.7+) no longer

> accept custom `temperature`/`top\_p` values. This project targets

> `claude-sonnet-4-6`, which still supports them.



\## Sample output



\*\*Input:\*\* AquaPure Mini, Instagram, playful tone



```

Your tap water just got served. 💧😎



Meet AquaPure Mini — the countertop glow-up your kitchen didn't know it

needed. Zaps 99% of contaminants in literally 60 seconds. That's faster

than you deciding what to watch on Netflix.



No plumber. No PhD required. Just plug, pour, and sip like the hydrated

icon you are. ✨



Clean water, tiny footprint, zero drama.



Ready to upgrade your sip? Tap the link and filter your first glass

today. 🚀



\#AquaPureMini #CleanWaterDaily #HydrateSmart #KitchenUpgrade #WaterFilter

\#DrinkClean #SmallSpaceBigImpact #FilteredNotFussy

```



\## Project structure



```

copywriter/

├── copy\_transformer.py   # main script

├── .gitignore             # excludes .env from version control

└── README.md

```



\## Skills demonstrated



\- Dynamic prompt template compilation

\- Inference parameter (temperature / top\_p) tuning

\- Platform-specific text generation via LLM API
