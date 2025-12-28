import streamlit as st
from google import genai
from google.genai import types
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Chat with Usama", page_icon="💬")
st.title("💬 Chat with 'FriendBot'")

# --- 1. SETUP API & LOAD DATA ---
# (Best practice: Store your key in a .env file or Streamlit secrets for production)

import os

# Try to get the key from Streamlit secrets, otherwise from environment variables
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = os.environ.get("GEMINI_API_KEY")

@st.cache_resource
def get_client():
    return genai.Client(api_key=API_KEY)

@st.cache_resource
def load_system_instruction():
    # Try to load the chat history file
    try:
        with open("chat_history.txt", "r", encoding="utf-8") as f:
            chat_log = f.read()
    except FileNotFoundError:
        return "You are a helpful assistant." # Fallback if file is missing

    return f"""
You are a chatbot simulating a person based on the attached chat logs. 
You are a chatbot simulating a person based on the attached chat logs. 
The chat is in chronological order. Do not reply randomly. 
Your goal is to reply to messages in roman Urdu exactly as the person named 'Shami' would.

Here are the rules:
1. Analyze the chat history below to understand 'Shami' tone, slang, sentence length, and humor.
2. Do not be overly polite or robotic. Be casual. 
3. If the chat history shows they use lowercase or emojis, do that.

--- START OF CHAT HISTORY ---
{chat_log}
--- END OF CHAT HISTORY ---
"""

client = get_client()
system_instruction = load_system_instruction()

# --- 2. INITIALIZE CHAT HISTORY ---
# This keeps the messages on screen when the app refreshes
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Start the actual Gemini chat session in the background
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_NONE"
                ),
            ]
        )
    )

# --- 3. DISPLAY CHAT INTERFACE ---
# Draw previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. HANDLE USER INPUT ---
if prompt := st.chat_input("Type a message..."):
    # A. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # B. Generate & Display Friend Response
    with st.chat_message("assistant"):
        with st.spinner("Friend is typing..."):
            # Send message to Gemini
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
