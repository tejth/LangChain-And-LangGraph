
import os
import time

import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# =========================================================
# CHECK API KEYS
# =========================================================

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing in your .env file.")
    st.stop()

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is missing in your .env file.")
    st.stop()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PDF Document Q&A",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("📚 PDF Document Q&A")

st.write(
    "Upload PDF files to the folder, create the vector store, "
    "and ask questions about your documents."
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectors" not in st.session_state:
    st.session_state.vectors = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    pdf_folder = st.text_input(
        "PDF Folder",
        value="./us_Census"
    )

    st.divider()

    chunk_size = st.slider(
        "Chunk Size",
        500,
        2000,
        1000,
        100
    )

    chunk_overlap = st.slider(
        "Chunk Overlap",
        0,
        500,
        100,
        50
    )

    number_of_results = st.slider(
        "Relevant Chunks",
        1,
        10,
        3
    )

    st.divider()

    create_button = st.button(
        "🔄 Create Vector Store",
        use_container_width=True
    )

    clear_button = st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    )


# =========================================================
# CLEAR CHAT
# =========================================================

if clear_button:

    st.session_state.messages = []

    st.rerun()


# =========================================================
# LLM
# =========================================================

@st.cache_resource
def get_llm():

    return ChatGroq(
        api_key=GROQ_API_KEY,

        # Current Groq production model
        model="openai/gpt-oss-20b",

        temperature=0
    )


# =========================================================
# GOOGLE EMBEDDINGS
# =========================================================

@st.cache_resource
def get_embeddings():

    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2",
        google_api_key=GOOGLE_API_KEY
    )


# =========================================================
# CREATE VECTOR STORE
# =========================================================

def create_vector_store():

    # -----------------------------------------------------
    # Check folder
    # -----------------------------------------------------

    if not os.path.exists(pdf_folder):

        st.error(
            f"❌ Folder does not exist: {pdf_folder}"
        )

        return None


    # -----------------------------------------------------
    # Load PDFs
    # -----------------------------------------------------

    loader = PyPDFDirectoryLoader(
        pdf_folder
    )

    documents = loader.load()


    if not documents:

        st.error(
            "❌ No PDF files found in the folder."
        )

        return None


    # -----------------------------------------------------
    # Split Documents
    # -----------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(
        documents
    )


    # -----------------------------------------------------
    # Create Embeddings
    # -----------------------------------------------------

    embeddings = get_embeddings()


    # -----------------------------------------------------
    # Create FAISS Vector Store
    # -----------------------------------------------------

    vectors = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )


    return vectors, documents, chunks


# =========================================================
# CREATE VECTOR STORE
# =========================================================

if create_button:

    with st.spinner(
        "📖 Reading PDFs and creating embeddings..."
    ):

        start_time = time.perf_counter()

        try:

            result = create_vector_store()

            if result:

                vectors, documents, chunks = result

                st.session_state.vectors = vectors

                st.session_state.documents = documents

                st.session_state.chunks = chunks

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                st.success(
                    "✅ Vector Store Created Successfully!"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "PDF Pages",
                        len(documents)
                    )

                with col2:

                    st.metric(
                        "Text Chunks",
                        len(chunks)
                    )

                with col3:

                    st.metric(
                        "Time",
                        f"{elapsed:.2f}s"
                    )

        except Exception as e:

            st.error(
                "❌ Error while creating Vector Store"
            )

            st.exception(e)


# =========================================================
# VECTOR STORE STATUS
# =========================================================

if st.session_state.vectors is not None:

    st.success(
        "🟢 Vector Store Ready"
    )

else:

    st.info(
        "👈 Click 'Create Vector Store' from the sidebar."
    )


# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask a question about your PDFs..."
)


# =========================================================
# PROCESS QUESTION
# =========================================================

if question:

    # -----------------------------------------------------
    # Check Vector Store
    # -----------------------------------------------------

    if st.session_state.vectors is None:

        st.warning(
            "⚠️ Please create the Vector Store first."
        )

        st.stop()


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # -----------------------------------------------------
    # RETRIEVER
    # -----------------------------------------------------

    retriever = (
        st.session_state.vectors
        .as_retriever(
            search_kwargs={
                "k": number_of_results
            }
        )
    )


    # -----------------------------------------------------
    # SEARCH DOCUMENTS
    # -----------------------------------------------------

    with st.spinner(
        "🔍 Searching documents..."
    ):

        start_time = time.perf_counter()

        retrieved_documents = retriever.invoke(
            question
        )


    # -----------------------------------------------------
    # CREATE CONTEXT
    # -----------------------------------------------------

    context = "\n\n".join(
        document.page_content
        for document in retrieved_documents
    )


    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are a helpful PDF document question-answering assistant.

Answer the user's question using ONLY the information
provided in the context.

Do not use outside knowledge.

Do not make up information.

If the answer is not present in the documents, say:

"The answer is not available in the provided documents."

Give a clear and concise answer.

================ CONTEXT ================

{context}

================ QUESTION ================

{question}
"""


    # -----------------------------------------------------
    # GENERATE ANSWER
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 Generating answer..."
        ):

            try:

                llm = get_llm()

                response = llm.invoke(
                    prompt
                )

                answer = response.content

                elapsed = (
                    time.perf_counter()
                    - start_time
                )


                # -------------------------------------------------
                # ANSWER
                # -------------------------------------------------

                st.markdown(
                    answer
                )

                st.caption(
                    f"⏱️ Response time: {elapsed:.2f} seconds"
                )


                # -------------------------------------------------
                # SOURCES
                # -------------------------------------------------

                if retrieved_documents:

                    with st.expander(
                        "📄 View Retrieved Sources"
                    ):

                        for index, document in enumerate(
                            retrieved_documents,
                            start=1
                        ):

                            source = document.metadata.get(
                                "source",
                                "Unknown document"
                            )

                            page = document.metadata.get(
                                "page"
                            )


                            filename = os.path.basename(
                                source
                            )


                            if page is not None:

                                st.markdown(
                                    f"**Source {index}:** "
                                    f"{filename} | "
                                    f"Page {page + 1}"
                                )

                            else:

                                st.markdown(
                                    f"**Source {index}:** "
                                    f"{filename}"
                                )


                            st.write(
                                document.page_content
                            )

                            st.divider()


                # -------------------------------------------------
                # SAVE ASSISTANT MESSAGE
                # -------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


            except Exception as e:

                st.error(
                    "❌ Error while generating the answer."
                )

                st.exception(e)
