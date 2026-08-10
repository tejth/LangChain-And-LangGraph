from dotenv import load_dotenv
load_dotenv()

import os
import io

import streamlit as st
import fitz  # PyMuPDF

from google import genai
from google.genai import types


# =========================================================
# GEMINI API SETUP
# =========================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is missing from your .env file.")
    st.stop()

client = genai.Client(
    api_key=GOOGLE_API_KEY
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "resume_images" not in st.session_state:
    st.session_state.resume_images = []

if "resume_name" not in st.session_state:
    st.session_state.resume_name = ""

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# PDF TO IMAGE FUNCTION
# =========================================================

def input_pdf_setup(uploaded_file):

    pdf_bytes = uploaded_file.read()

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    images = []

    for page in pdf:

        # Render page at good quality
        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )

        # Convert page to JPEG bytes
        image_bytes = pix.tobytes(
            "jpeg"
        )

        images.append(image_bytes)

    pdf.close()

    return images


# =========================================================
# GEMINI RESPONSE FUNCTION
# =========================================================

def get_gemini_response(
    user_input,
    resume_images,
    system_prompt
):

    contents = []

    # Add instruction/prompt
    contents.append(system_prompt)

    # Add user's input
    contents.append(user_input)

    # Add all resume pages
    for image_bytes in resume_images:

        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            )
        )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=contents
    )

    return response.text


# =========================================================
# ATS ANALYSIS PROMPT
# =========================================================

ATS_PROMPT = """
You are an expert ATS (Applicant Tracking System)
resume analyzer and technical recruiter.

You will receive:

1. A Job Description
2. Images of a candidate's Resume

Analyze the candidate's resume against the job description.

Provide the following:

# ATS SCORE

Give an ATS match score from 0 to 100.

# MATCHING SKILLS

List the skills from the resume that match the job description.

# MISSING SKILLS

List important skills from the job description that are
missing from the resume.

# MATCHING KEYWORDS

List important keywords that appear in both the resume
and job description.

# MISSING KEYWORDS

List important job-description keywords that are absent
from the resume.

# EXPERIENCE MATCH

Explain how well the candidate's experience matches the role.

# PROJECT MATCH

Explain how relevant the candidate's projects are.

# EDUCATION MATCH

Explain whether the education matches the requirements.

# STRENGTHS

List the strongest aspects of the resume for this job.

# WEAKNESSES

List the major weaknesses.

# IMPROVEMENT SUGGESTIONS

Give practical suggestions to improve the resume for this
specific job.

# FINAL RECOMMENDATION

Give a short overall recommendation.

IMPORTANT:

- Only use information visible in the resume and job description.
- Never invent skills, experience, education, or projects.
- Do not assume something is present if it is not visible.
- Be accurate.
"""


# =========================================================
# QUESTION ANSWERING PROMPT
# =========================================================

QUESTION_PROMPT = """
You are an AI resume assistant.

You will receive:

1. A Job Description
2. Images of the candidate's Resume
3. A question from the user

Answer the user's question using ONLY the information
available in the resume and job description.

Rules:

- Do not invent information.
- If the answer is not available, clearly say:
  "I cannot find this information in the provided resume
   or job description."
- Be accurate.
- Keep the answer clear and easy to understand.
"""


# =========================================================
# TITLE
# =========================================================

st.title("📄 ATS Resume Analyzer")

st.write(
    "Analyze your resume against a job description "
    "and ask questions about your resume."
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📌 How It Works")

    st.write("1️⃣ Enter Job Description")
    st.write("2️⃣ Upload Resume PDF")
    st.write("3️⃣ Convert PDF to Images")
    st.write("4️⃣ Analyze with Gemini")
    st.write("5️⃣ Ask Questions")

    st.divider()

    st.info(
        "PDF processing uses PyMuPDF. "
        "Poppler is NOT required."
    )


# =========================================================
# JOB DESCRIPTION
# =========================================================

st.subheader("1️⃣ Job Description")

job_description = st.text_area(
    "Paste the Job Description",
    height=250,
    placeholder=(
        "Paste the complete job description here..."
    )
)


# =========================================================
# RESUME UPLOAD
# =========================================================

st.subheader("2️⃣ Upload Resume")

uploaded_file = st.file_uploader(
    "Upload your resume in PDF format",
    type=["pdf"]
)


# =========================================================
# PROCESS RESUME
# =========================================================

if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button(
        "📑 Process Resume",
        use_container_width=True
    ):

        with st.spinner(
            "Processing your resume..."
        ):

            try:

                resume_images = input_pdf_setup(
                    uploaded_file
                )

                st.session_state.resume_images = (
                    resume_images
                )

                st.session_state.resume_name = (
                    uploaded_file.name
                )

                st.session_state.analysis = None

                st.session_state.chat_history = []

                st.success(
                    f"Resume processed successfully! "
                    f"{len(resume_images)} page(s) found."
                )

            except Exception as e:

                st.error(
                    "❌ Error while processing the PDF."
                )

                st.exception(e)


# =========================================================
# RESUME STATUS
# =========================================================

if st.session_state.resume_images:

    st.success(
        f"✅ Resume ready: "
        f"{st.session_state.resume_name} | "
        f"{len(st.session_state.resume_images)} page(s)"
    )


# =========================================================
# RESUME PREVIEW
# =========================================================

if st.session_state.resume_images:

    with st.expander("👀 Preview Resume"):

        for i, image_bytes in enumerate(
            st.session_state.resume_images
        ):

            st.image(
                image_bytes,
                caption=f"Resume Page {i + 1}",
                use_container_width=True
            )


# =========================================================
# ATS ANALYSIS
# =========================================================

st.divider()

st.subheader("3️⃣ ATS Analysis")

if st.button(
    "🚀 Analyze Resume",
    use_container_width=True
):

    if not job_description.strip():

        st.warning(
            "Please enter a Job Description first."
        )

        st.stop()

    if not st.session_state.resume_images:

        st.warning(
            "Please upload and process your resume first."
        )

        st.stop()

    user_input = f"""
JOB DESCRIPTION:

{job_description}

Please analyze the attached resume against this
job description.
"""

    with st.spinner(
        "🤖 Gemini is analyzing your resume..."
    ):

        try:

            analysis = get_gemini_response(
                user_input,
                st.session_state.resume_images,
                ATS_PROMPT
            )

            st.session_state.analysis = analysis

        except Exception as e:

            st.error(
                "❌ Gemini API error."
            )

            st.exception(e)


# =========================================================
# DISPLAY ATS ANALYSIS
# =========================================================

if st.session_state.analysis:

    st.subheader("📊 ATS Analysis")

    st.markdown(
        st.session_state.analysis
    )


# =========================================================
# QUESTION ANSWERING
# =========================================================

if st.session_state.resume_images:

    st.divider()

    st.subheader(
        "4️⃣ Ask Questions About Your Resume"
    )

    question = st.text_input(
        "Ask a question",
        placeholder=(
            "Example: Which of my skills match this job?"
        )
    )

    if st.button(
        "💬 Ask Gemini",
        use_container_width=True
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

            st.stop()

        user_input = f"""
JOB DESCRIPTION:

{job_description}


USER QUESTION:

{question}
"""

        with st.spinner(
            "🤖 Gemini is thinking..."
        ):

            try:

                answer = get_gemini_response(
                    user_input,
                    st.session_state.resume_images,
                    QUESTION_PROMPT
                )

                st.session_state.chat_history.append(
                    {
                        "question": question,
                        "answer": answer
                    }
                )

            except Exception as e:

                st.error(
                    "❌ Gemini API error."
                )

                st.exception(e)


# =========================================================
# CHAT HISTORY
# =========================================================

if st.session_state.chat_history:

    st.divider()

    st.subheader("💬 Chat History")

    for chat in st.session_state.chat_history:

        st.markdown(
            f"**👤 You:** {chat['question']}"
        )

        st.markdown(
            f"**🤖 Gemini:** {chat['answer']}"
        )

        st.divider()


# =========================================================
# CLEAR BUTTON
# =========================================================

if st.session_state.resume_images:

    if st.button(
        "🗑️ Clear Resume & Start Again"
    ):

        st.session_state.resume_images = []
        st.session_state.resume_name = ""
        st.session_state.analysis = None
        st.session_state.chat_history = []

        st.rerun()