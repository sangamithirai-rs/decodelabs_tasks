# Image Generation Studio

A Python CLI tool that generates images from text prompts using the [Pollinations.ai](https://pollinations.ai) API — built as Project 3 of the Generative AI Industrial Training Kit (DecodeLabs, Batch 2026).

## What it does

Takes a text prompt and aspect ratio, sends a request to an image generation API, and saves the result locally — with production-grade reliability built in:

- **Aspect ratio mapping** — translates friendly names (`square`, `landscape`, `portrait`) into exact supported resolutions
- **Timeout handling** — explicit connect/read timeouts so the program never hangs indefinitely on a dead connection
- **Retry with exponential backoff** — automatically retries failed requests with increasing delays instead of giving up immediately or hammering the server
- **Integrity verification** — forces a full pixel-level decode of the saved image with Pillow to catch truncated or corrupted downloads that a simple header check would miss

## Setup

```bash
git clone https://github.com/rssangamithirai-glitch/image-generation-studio.git
cd image-generation-studio
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
```

## Usage

```bash
python generate.py "a cat astronaut, watercolor style" --aspect landscape
```

**Arguments:**
| Flag | Description | Default |
|---|---|---|
| `prompt` | Text description of the image (required) | — |
| `--aspect` | `square`, `landscape`, or `portrait` | `square` |

Output is saved as `output.png` in the current directory.

## Example

Prompt: `"a cat astronaut, watercolor style"`

![Generated image](Task-3-image-generation-studio/output.png)

## What I learned

This project was less about "calling an AI API" and more about the engineering discipline around it — handling network failures gracefully, verifying data integrity, and designing for retries without overwhelming the server. That reliability layer is what separates a script that works in a demo from one that works in production.

## Tech stack

- Python 3
- `requests` — HTTP calls
- `Pillow` — image integrity verification
