"""
DecodeLabs Generative AI - Project 1
Custom AI Chatbot with Memory

This script connects to Google's Gemini API and maintains conversation
history in an in-memory list, so the chatbot remembers earlier messages
during the same session.
"""

import os
from dotenv import load_dotenv
from google import genai

# Step 1: Load the API key from the .env file into the environment.
# This keeps the key out of the source code itself.
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Make sure it's set in your .env file."
    )

# Step 2: Create the Gemini client using our API key.
client = genai.Client(api_key=api_key)

# The model we're using. gemini-3.5-flash is fast and free-tier friendly.
MODEL_NAME = "gemini-3.5-flash"

# Maximum number of messages (user + model combined) to keep in history.
# Once exceeded, the oldest messages are dropped (FIFO) so we never send
# an unbounded amount of text to the API.
MAX_HISTORY_MESSAGES = 20

# Step 3: This is the "memory" - a plain Python list that lives only
# for as long as this program runs. Every user message and every model
# reply gets appended here, and the WHOLE list is sent on every request.
conversation_history = []


def add_to_history(role, text):
    """Append a single message to the in-memory conversation history,
    then trim the oldest messages if we've grown past the limit."""
    conversation_history.append({
        "role": role,
        "parts": [{"text": text}]
    })

    # FIFO truncation: if we're over the limit, drop messages from the
    # front of the list (the oldest ones) until we're back within it.
    while len(conversation_history) > MAX_HISTORY_MESSAGES:
        conversation_history.pop(0)


def get_model_reply():
    """Send the full conversation history to Gemini and return its reply."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=conversation_history,
    )
    return response.text


def main():
    print("=" * 50)
    print("DecodeLabs Chatbot with Memory (Gemini)")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Chatbot: Goodbye!")
            break

        if not user_input:
            # Skip empty input instead of wasting an API call.
            continue

        # Step 4: Append the user's message to history BEFORE calling the API,
        # so the model sees it as part of the conversation.
        add_to_history("user", user_input)

        try:
            reply = get_model_reply()
        except Exception as error:
            print(f"\n[Error contacting Gemini API: {error}]")
            # Remove the user message we just added, since it never
            # got a matching reply - keeps history consistent.
            conversation_history.pop()
            continue

        # Step 5: Append the model's reply to history too, so it's
        # remembered in the next turn.
        add_to_history("model", reply)

        print(f"\nChatbot: {reply}")


if __name__ == "__main__":
    main()