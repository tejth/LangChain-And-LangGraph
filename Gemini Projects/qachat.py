
from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from google import genai


# -----------------------------
# Gemini Client
# -----------------------------

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# -----------------------------
# Function to get Gemini response
# -----------------------------

def get_response(prompt, history):

    # Send previous conversation + new prompt
    contents = []

    for message in history:
        contents.append({
            "role": message["role"],
            "parts": [{"text": message["content"]}]
        })

    contents.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents
    )

    return response.text


# -----------------------------
# Streamlit App
# -----------------------------

st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖"
)

st.title("Gemini Chatbot 🤖")


# -----------------------------
# Initialize Chat History
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Display Previous Messages
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# -----------------------------
# User Input
# -----------------------------

prompt = st.chat_input("Type your message...")


if prompt:

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })


    # Generate Gemini response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = get_response(
                prompt,
                st.session_state.messages[:-1]
            )

            st.write(response)


    # Save Gemini response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
