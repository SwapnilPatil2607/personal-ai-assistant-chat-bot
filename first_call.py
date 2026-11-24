
"""Your first call to a language model.

Run it from the terminal:
    python first_call.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

MODEL = "inclusionai/ling-3.2-flash:free"

# Load API key
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "API key not found. Check your .env file."
    )

# Connect to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Conversation
messages = [
    {
        "role": "system",
        "content": (
            "You are a grumpy pirate. "
            "Answer in one or two sentences."
        ),
    },
    {
        "role": "user",
        "content": "What's the best way to learn to code?",
    },
]

# Send request
try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=200,
    )

    reply = response.choices[0].message.content

    if not reply or not reply.strip():
        print("The model returned an empty response.")
    else:
        print("\nCaptain's response:")
        print(reply.strip())

except Exception as error:
    print(error)
    print(f"Something went wrong: {error}")
