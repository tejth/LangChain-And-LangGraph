from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from google import genai
from google.genai import types


# ==========================================
# Gemini Configuration
# ==========================================

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("GOOGLE_API_KEY is missing from your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# ==========================================
# Gemini Vision Function
# ==========================================

def get_nutrition_response(image_bytes, mime_type, question):

    prompt = f"""
You are an AI Nutrition Assistant.

Analyze the food image carefully.

Identify the visible food items and provide an approximate
nutrition analysis.

For every food item provide:

1. Food name
2. Estimated portion size
3. Estimated calories
4. Protein
5. Carbohydrates
6. Fat
7. Fiber

Then provide:

- Total estimated calories
- Total protein
- Total carbohydrates
- Total fat
- Total fiber
- A short health/nutrition observation

Important instructions:

- Values are estimates because exact portion sizes and ingredients
  cannot always be determined from an image.
- Do not pretend the values are medically exact.
- If a food item cannot be identified confidently, say so.
- Do not diagnose diseases or medical conditions.
- Keep the answer simple and easy to understand.

The user may also ask a specific question about the food.

User question:
{question}
"""

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            image_part,
            prompt
        ]
    )

    return response.text


# ==========================================
# Streamlit Configuration
# ==========================================

st.set_page_config(
    page_title="AI Nutrition Assistant",
    page_icon="🥗",
    layout="centered"
)


# ==========================================
# UI
# ==========================================

st.title("🥗 AI Nutrition Assistant")

st.write(
    "Upload a food image and Gemini will identify the food items "
    "and provide an approximate calorie and nutrition analysis."
)


# ==========================================
# Upload Image
# ==========================================

uploaded_file = st.file_uploader(
    "📷 Upload your food image",
    type=["jpg", "jpeg", "png", "webp"]
)


# ==========================================
# When Image is Uploaded
# ==========================================

if uploaded_file:

    st.success("Food image uploaded successfully!")

    st.image(
        uploaded_file,
        caption="Uploaded Food Image",
        use_container_width=True
    )

    # --------------------------------------
    # Read Image
    # --------------------------------------

    image_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type

    # --------------------------------------
    # Initial Analysis
    # --------------------------------------

    if st.button("🔍 Analyze Food"):

        with st.spinner("Gemini is analyzing your food..."):

            try:

                analysis = get_nutrition_response(
                    image_bytes,
                    mime_type,
                    "Analyze this complete food image and provide the nutrition information."
                )

                st.session_state.food_analysis = analysis

            except Exception as e:

                st.error(
                    f"Error while analyzing the image: {e}"
                )


    # ======================================
    # Display Analysis
    # ======================================

    if "food_analysis" in st.session_state:

        st.subheader("🍽️ Nutrition Analysis")

        st.write(
            st.session_state.food_analysis
        )


    # ======================================
    # Chat History
    # ======================================

    if "nutrition_messages" not in st.session_state:

        st.session_state.nutrition_messages = []


    # ======================================
    # Display Previous Messages
    # ======================================

    for message in st.session_state.nutrition_messages:

        with st.chat_message(message["role"]):

            st.write(message["content"])


    # ======================================
    # Ask Question
    # ======================================

    question = st.chat_input(
        "Ask something about this food..."
    )


    if question:

        # Show user question

        with st.chat_message("user"):

            st.write(question)


        st.session_state.nutrition_messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # Generate Answer

        with st.chat_message("assistant"):

            with st.spinner("Analyzing your question..."):

                try:

                    answer = get_nutrition_response(
                        image_bytes,
                        mime_type,
                        question
                    )

                    st.write(answer)

                    st.session_state.nutrition_messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )


else:

    st.info(
        "👆 Upload a food image to start the nutrition analysis."
    )