
from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from google import genai
from PyPDF2 import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter

import chromadb


# ==========================================
# Gemini Client
# ==========================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================
# ChromaDB
# ==========================================

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(
    name="pdf_documents"
)


# ==========================================
# Extract Text from PDF
# ==========================================

def extract_text(pdf_file):

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


# ==========================================
# Create Gemini Embedding
# ==========================================

def create_embedding(text):

    result = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )

    return result.embeddings[0].values


# ==========================================
# Process PDFs
# ==========================================

def process_pdfs(pdf_files):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    for pdf in pdf_files:

        # Extract text
        text = extract_text(pdf)

        # Split text into chunks
        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):

            # Create embedding
            embedding = create_embedding(chunk)

            # Store in ChromaDB
            collection.add(
                ids=[
                    f"{pdf.name}_{i}"
                ],
                documents=[
                    chunk
                ],
                embeddings=[
                    embedding
                ],
                metadatas=[
                    {
                        "source": pdf.name
                    }
                ]
            )


# ==========================================
# Ask Gemini
# ==========================================

def ask_gemini(question, context):

    prompt = f"""
You are a helpful PDF chatbot.

Answer the user's question using ONLY
the information provided from the uploaded PDFs.

If the answer is not available in the PDFs,
say:

"The information is not available
in the uploaded documents."

PDF information:

{context}

User question:

{question}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# Streamlit App
# ==========================================

st.set_page_config(
    page_title="Multi PDF Chatbot",
    page_icon="📚"
)

st.title("📚 Multi PDF Chatbot")

st.write(
    "Upload multiple PDF files and ask questions about them."
)


# ==========================================
# Upload PDFs
# ==========================================

pdf_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# ==========================================
# Process PDFs
# ==========================================

if pdf_files:

    st.write(
        f"📄 {len(pdf_files)} PDF(s) selected"
    )

    if st.button("Process PDFs"):

        with st.spinner(
            "Processing PDFs..."
        ):

            # Delete previous collection
            try:

                chroma_client.delete_collection(
                    name="pdf_documents"
                )

            except Exception:
                pass


            # Create new collection
            collection = (
                chroma_client.get_or_create_collection(
                    name="pdf_documents"
                )
            )


            # Save collection
            st.session_state.collection = collection


            # Process uploaded PDFs
            process_pdfs(pdf_files)


        st.success(
            "PDFs processed successfully!"
        )


# ==========================================
# Chat History
# ==========================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# ==========================================
# Chat Input
# ==========================================

question = st.chat_input(
    "Ask something about your PDFs..."
)


if question:

    # Check whether PDFs are processed

    if "collection" not in st.session_state:

        st.warning(
            "Please upload and process your PDFs first."
        )

    else:

        # ======================================
        # Display User Question
        # ======================================

        with st.chat_message("user"):

            st.write(question)


        # Save user message

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })


        # ======================================
        # Create Question Embedding
        # ======================================

        question_embedding = create_embedding(
            question
        )


        # ======================================
        # Search ChromaDB
        # ======================================

        results = st.session_state.collection.query(
            query_embeddings=[
                question_embedding
            ],
            n_results=4
        )


        # Get relevant chunks

        documents = results["documents"][0]


        # Combine chunks

        context = "\n\n".join(
            documents
        )


        # ======================================
        # Generate Answer
        # ======================================

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching PDFs..."
            ):

                answer = ask_gemini(
                    question,
                    context
                )

                st.write(answer)


        # Save answer

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
