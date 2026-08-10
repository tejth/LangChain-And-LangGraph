from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from google import genai

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key)


# Function to get response from Gemini
def get_response_from_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text


# Streamlit app
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖"
)

st.header("Gemini Chatbot 🤖")

input_text = st.text_input("Enter your prompt here:")

submit_button = st.button("Ask Gemini")

if submit_button and input_text:

    with st.spinner("Gemini is thinking..."):

        response = get_response_from_gemini(input_text)

        st.success("Gemini's Response:")
        st.write(response)