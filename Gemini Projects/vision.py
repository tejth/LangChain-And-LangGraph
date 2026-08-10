from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from google import genai
from PIL import Image


# Get API key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key)


# Function to get response from Gemini
def get_response_from_gemini(prompt, image):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            prompt,
            image
        ]
    )

    return response.text


# Streamlit app
st.set_page_config(
    page_title="Gemini Vision Chatbot",
    page_icon="👁️"
)

st.header("Gemini Vision Chatbot 👁️")


# Upload image
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)


# If image is uploaded
if uploaded_file is not None:

    # Open image
    image = Image.open(uploaded_file)

    # Display image
    st.image(
        image,
        caption="Uploaded Image",
        use_container_width=True
    )

    # Ask question
    input_text = st.text_input(
        "Ask something about this image:"
    )

    # Button
    submit_button = st.button("Analyze Image")

    # Generate response
    if submit_button and input_text:

        with st.spinner("Gemini is analyzing the image..."):

            response = get_response_from_gemini(
                input_text,
                image
            )

            st.success("Gemini's Response:")
            st.write(response)

elif uploaded_file is None:

    st.info("Please upload an image to get started.")
