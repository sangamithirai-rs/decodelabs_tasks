# DecodeLabs Generative AI Project 4: Intelligent Code Reviewer & Explainer

A CLI tool that reads a `.py`, `.js`, or `.java` file, sends it to a
Generative AI model (Google Gemini) with a strict "Senior QA Engineer"
system instruction, validates the structured response, and renders a
bug report plus a refactored version of the code straight to the terminal.

## Pipeline

CODE FILE
-> FILE INGESTION (file_handler.py)
-> RAW CODE STRING
-> GENERATIVE AI (ai_engine.py)
-> STRUCTURED AI RESPONSE
-> RESPONSE VALIDATION (validator.py)
-> MARKDOWN RENDERING (renderer.py)
-> TERMINAL OUTPUT

## Files

| File | Responsibility |
|---|---|
| `main.py` | Orchestrates the pipeline end to end |
| `file_handler.py` | Reads code files, validates extensions, handles I/O errors |
| `ai_engine.py` | Talks to the Gemini API only |
| `validator.py` | Enforces the `## BUG_REPORT` / `## REFACTORED_CODE` structure |
| `renderer.py` | Prints validated Markdown to the terminal via `rich` |
| `exceptions.py` | Shared custom exception types |
| `samples/` | Sample buggy `.py` / `.js` files to test with |

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env and add your real key
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
(no credit card required for the free tier).

Your `.env` should look like:
GEMINI_API_KEY=your-real-key-here
REVIEWER_MODEL=gemini-3.6-flash

## Run

```bash
python main.py samples/buggy_sample.py
python main.py samples/buggy_sample.js
```

Or run with no arguments to be prompted for a path:

```bash
python main.py
```

## Example Output
BUG_REPORT
Security Vulnerability: SQL injection vulnerability in get_user_data
caused by constructing SQL queries via string concatenation instead
of parameterized queries.
Security Vulnerability: Hardcoded credential password = "admin123"
embedded directly in source code.
Logical Error / Exception: calculate_average raises a
ZeroDivisionError when passed an empty list.
REFACTORED_CODE

def get_user_data(db, user_id):
query = "SELECT * FROM users WHERE id = %s"
return db.execute(query, (user_id,))
...

## Error Handling

The tool safely handles and reports:

- Missing files (`FileNotFoundError`)
- Permission issues (`PermissionError`)
- Non-UTF-8 / unreadable files (`UnicodeDecodeError`)
- Unsupported file extensions (only `.py`, `.js`, `.java` are supported)
- Malformed AI responses that don't match the required output structure

Example:

```bash
python main.py samples/does_not_exist.py
# [File Error] File not found: 'samples/does_not_exist.py'

python main.py requirements.txt
# [Unsupported File Type] Unsupported file extension '.txt'. Supported extensions are: .java, .js, .py
```

## Notes

- The API key is read only from the `GEMINI_API_KEY` environment variable
  (or a local `.env` file via `python-dotenv`). It is never hardcoded
  anywhere in the source.
- The AI is instructed to act as a cold, analytical QA engineer -- no
  greetings, no filler, no invented bugs. It always returns exactly two
  sections: `## BUG_REPORT` and `## REFACTORED_CODE`.
- Supported extensions: `.py`, `.js`, `.java`.
