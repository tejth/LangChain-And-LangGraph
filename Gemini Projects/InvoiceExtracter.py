from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st

from google import genai
from google.genai import types


# =========================================================
# GEMINI CLIENT
# =========================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error(
        "GOOGLE_API_KEY is missing from your .env file."
    )
    st.stop()

client = genai.Client(
    api_key=GOOGLE_API_KEY
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Multi-Language Invoice Extractor",
    page_icon="🧾",
    layout="centered"
)


# =========================================================
# INVOICE RESPONSE FUNCTION
# =========================================================

def get_invoice_response(question, invoice):

    # Get invoice bytes
    invoice_bytes = invoice.getvalue()

    # Get MIME type
    mime_type = invoice.type

    prompt = """
You are a Multi-Language Invoice Assistant.

Your job is to analyze the uploaded invoice and answer
questions about it.

The invoice can be written in any language.

Understand the invoice regardless of its language.

Answer the user's question using ONLY information
present in the uploaded invoice.

You can answer questions such as:

- What is the invoice date?
- What is the invoice number?
- What is the total amount?
- What is the subtotal?
- What is the tax amount?
- What is the customer's name?
- What is the seller's name?
- What is the billing address?
- What is the shipping address?
- What products are listed?
- What is the quantity of each product?
- What is the price of a product?
- What currency is used?
- What is the due date?
- What payment method is mentioned?

IMPORTANT RULES:

1. Do not invent information.
2. Do not make assumptions.
3. Use only information visible in the invoice.
4. If the requested information is not present,
   say that the information is not available.
5. Keep the answer simple and accurate.
6. If the invoice uses another language, understand it
   and answer the user in the language used by the user.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[
            prompt,

            types.Part.from_bytes(
                data=invoice_bytes,
                mime_type=mime_type
            ),

            question
        ]
    )

    return response.text


# =========================================================
# TITLE
# =========================================================

st.title(
    "🧾 Multi-Language Invoice Extractor"
)

st.write(
    "Upload an invoice and ask questions about it."
)

st.divider()


# =========================================================
# FILE UPLOADER
# =========================================================

uploaded_file = st.file_uploader(
    "📤 Upload your invoice",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
        "pdf"
    ]
)


# =========================================================
# CHAT HISTORY
# =========================================================

if "invoice_messages" not in st.session_state:

    st.session_state.invoice_messages = []


# =========================================================
# INVOICE UPLOADED
# =========================================================

if uploaded_file:

    st.success(
        f"✅ Invoice uploaded: {uploaded_file.name}"
    )


    # =====================================================
    # DISPLAY IMAGE
    # =====================================================

    if uploaded_file.type.startswith("image"):

        st.image(
            uploaded_file,
            caption="Uploaded Invoice",
            use_container_width=True
        )


    # =====================================================
    # DISPLAY PDF
    # =====================================================

    elif uploaded_file.type == "application/pdf":

        st.info(
            "📄 PDF invoice uploaded successfully."
        )


    st.divider()


    # =====================================================
    # CHAT HISTORY DISPLAY
    # =====================================================

    for message in st.session_state.invoice_messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # =====================================================
    # QUESTION INPUT
    # =====================================================

    question = st.chat_input(
        "Ask something about the invoice..."
    )


    # =====================================================
    # PROCESS QUESTION
    # =====================================================

    if question:

        # -----------------------------------------------
        # Display user question
        # -----------------------------------------------

        with st.chat_message("user"):

            st.write(question)


        # -----------------------------------------------
        # Save user question
        # -----------------------------------------------

        st.session_state.invoice_messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # -----------------------------------------------
        # Generate Gemini response
        # -----------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "🔍 Analyzing invoice..."
            ):

                try:

                    answer = get_invoice_response(
                        question,
                        uploaded_file
                    )

                    st.write(answer)

                except Exception as e:

                    answer = (
                        "Sorry, I could not analyze "
                        "the invoice."
                    )

                    st.error(answer)

                    st.exception(e)


        # -----------------------------------------------
        # Save assistant response
        # -----------------------------------------------

        st.session_state.invoice_messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# =========================================================
# NO INVOICE
# =========================================================

else:

    st.info(
        "👆 Please upload an invoice to start."
    )