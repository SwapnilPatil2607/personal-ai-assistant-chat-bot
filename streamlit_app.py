
"""
Your personal AI assistant.

Run it from the terminal:
    streamlit run app.py
"""

import os
import sqlite3

import openai
import streamlit as st
from dotenv import load_dotenv

# ---------- Personality ----------
TITLE = "Speak with Captain Jack Sparrow"

SYSTEM_PROMPT = """
You are Captain Jack Sparrow from Pirates of the Caribbean.

Personality:
- Speak like Captain Jack Sparrow.
- Be witty, clever, humorous, and slightly sarcastic.
- Use pirate expressions naturally.
- Stay in character throughout the conversation.
- Keep answers short, usually two or three sentences.
- Remember the context of the conversation.
"""

# ---------- Settings ----------
MODEL = "google/gemma-4-26b-a4b-it:floor"
MAX_REPLY_TOKENS = 300
MAX_MESSAGES = 20
DB_NAME = "chat_history.db"

# ---------- API Setup ----------
load_dotenv()

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# ---------- Database Setup ----------
def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def load_messages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, content FROM messages ORDER BY id"
    )

    messages = [
        {"role": row[0], "content": row[1]}
        for row in cursor.fetchall()
    ]

    conn.close()
    return messages


def save_message(role, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages (role, content) VALUES (?, ?)",
        (role, content)
    )

    conn.commit()
    conn.close()


def clear_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM messages")

    conn.commit()
    conn.close()


# Initialize database
init_database()

# ---------- Page UI ----------
st.set_page_config(
    page_title=TITLE,
    page_icon="🏴‍☠️",
    layout="centered"
)

st.title(TITLE)
st.caption("Your personal pirate AI assistant. Arrr!")

# ---------- Session Memory ----------
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# ---------- Clear Chat ----------
col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_database()
        st.session_state.messages = []
        st.rerun()

# ---------- Display Conversation ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ---------- Message Limit ----------
messages_sent = sum(
    1 for m in st.session_state.messages
    if m["role"] == "user"
)

if messages_sent >= MAX_MESSAGES:
    st.info(
        "You've reached the message limit for this chat. "
        "Clear the chat to start a new adventure!"
    )
    st.stop()

# ---------- Chat Input ----------
user_text = st.chat_input("Say something, matey...")

if user_text:

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_text
    })

    with st.chat_message("user"):
        st.write(user_text)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Captain Jack is thinking..."):

                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        }
                    ] + st.session_state.messages,
                    max_tokens=MAX_REPLY_TOKENS,
                )

                reply = (
                    response.choices[0].message.content
                    or "(The model sent back an empty reply.)"
                )

                st.write(reply)

        # Save both messages only after successful API response
        save_message("user", user_text)
        save_message("assistant", reply)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

    except openai.APIError as error:

        # Remove failed user message from session memory
        st.session_state.messages.pop()

        st.error(f"Couldn't get a reply from the model: {error}")

    except Exception as error:

        st.session_state.messages.pop()

        st.error(f"Something went wrong: {error}")
