
# Custom AI Chatbot with Memory

DecodeLabs Industrial Training Kit — Generative AI Project 1.

A terminal-based chatbot that connects to Google's Gemini API and remembers
previous messages during a live session, by maintaining an in-memory list of
the conversation history and re-sending it with every request.

## How it works

Large language models are stateless — each API call is independent and has
no memory of previous calls. This project creates the *illusion* of memory by:

1. Storing every user message and model reply in a Python list
   (`conversation_history`) as the conversation happens.
2. Sending the **entire** history back to the API on every new request, not
   just the latest message.
3. Appending the new reply to the list, so the next request carries the full
   conversation so far.

## Setup

1. Clone this repo and open it in VS Code.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\Activate.ps1      # Windows PowerShell
   source venv/bin/activate       # macOS/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
   (no credit card required).
5. Create a `.env` file in the project root with:
   ```
   GEMINI_API_KEY=your_key_here
   ```
6. Run the chatbot:
   ```
   python chatbot.py
   ```

## Usage

Chat normally in the terminal. Type `exit` or `quit` to end the session.

Example:
```
You: my name is Sam
Chatbot: Nice to meet you, Sam!
You: what's my name?
Chatbot: Your name is Sam!
```

## Tech stack

- Python 3
- [google-genai](https://pypi.org/project/google-genai/) — official Gemini SDK
- python-dotenv — loads the API key from `.env`

## Notes

- `.env` is excluded via `.gitignore` and never committed — the API key stays
  local to each user's machine.
- The conversation history is in-memory only; it resets each time the
  program restarts (no persistence to disk or database).
