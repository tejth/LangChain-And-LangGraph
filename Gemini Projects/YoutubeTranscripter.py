from dotenv import load_dotenv
load_dotenv()

import os
import re
import streamlit as st

from google import genai
from youtube_transcript_api import YouTubeTranscriptApi


# ============================================================
# Gemini Configuration
# ============================================================

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("GOOGLE_API_KEY is missing from your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# ============================================================
# Extract YouTube Video ID
# ============================================================

def get_video_id(url):

    patterns = [
        r"(?:v=|youtu\.be/|youtube\.com/shorts/)([^&?/]+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


# ============================================================
# Get YouTube Transcript
# ============================================================

def get_transcript(video_id):

    try:

        ytt_api = YouTubeTranscriptApi()

        # Get all available transcripts
        transcript_list = ytt_api.list(video_id)

        transcript = None

        # ----------------------------------------------------
        # Try English first
        # ----------------------------------------------------

        try:

            transcript = transcript_list.find_transcript(
                ["en"]
            )

        except Exception:
            pass


        # ----------------------------------------------------
        # If English is unavailable, try Hindi
        # ----------------------------------------------------

        if transcript is None:

            try:

                transcript = transcript_list.find_transcript(
                    ["hi"]
                )

            except Exception:
                pass


        # ----------------------------------------------------
        # If English/Hindi unavailable,
        # use the first available transcript
        # ----------------------------------------------------

        if transcript is None:

            transcript = next(
                iter(transcript_list)
            )


        # ----------------------------------------------------
        # Fetch transcript
        # ----------------------------------------------------

        fetched_transcript = transcript.fetch()


        # ----------------------------------------------------
        # Convert transcript to plain text
        # ----------------------------------------------------

        text = " ".join(
            snippet.text
            for snippet in fetched_transcript
        )


        return text


    except Exception as e:

        return f"ERROR: {str(e)}"


# ============================================================
# Ask Gemini About Transcript
# ============================================================

def ask_gemini(transcript, question):

    prompt = f"""
You are an intelligent YouTube Video Question Answering Assistant.

You have been provided with the transcript of a YouTube video.

Your job is to answer the user's question using ONLY the
information available in the transcript.

IMPORTANT RULES:

1. Do not invent information.
2. Do not make assumptions that are not supported by the transcript.
3. If the answer is not available in the transcript, clearly say:
   "The answer is not available in the video transcript."
4. The transcript may be in Hindi, English, or another language.
5. Understand the transcript regardless of its language.
6. The user may ask questions in English or Hindi.
7. Answer in the same language used by the user whenever possible.
8. Keep the answer clear and easy to understand.
9. If the user asks for a summary, provide the important points.
10. If the user asks for an explanation, explain it based on the video.

================ VIDEO TRANSCRIPT ================

{transcript}

================ USER QUESTION ================

{question}

===================================================

Now answer the user's question.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ============================================================
# Streamlit Configuration
# ============================================================

st.set_page_config(
    page_title="YouTube Video Q&A",
    page_icon="🎥",
    layout="wide"
)


# ============================================================
# Application Title
# ============================================================

st.title("🎥 YouTube Video Q&A")

st.write(
    "Enter a YouTube video URL, extract its transcript, "
    "and ask questions about the video using Gemini."
)


# ============================================================
# Session State
# ============================================================

if "transcript" not in st.session_state:

    st.session_state.transcript = None


if "video_id" not in st.session_state:

    st.session_state.video_id = None


if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# YouTube URL Input
# ============================================================

youtube_url = st.text_input(
    "🔗 Enter YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=..."
)


# ============================================================
# Process Video
# ============================================================

if st.button(
    "🚀 Process Video",
    use_container_width=True
):

    if not youtube_url:

        st.warning(
            "Please enter a YouTube URL."
        )

    else:

        video_id = get_video_id(
            youtube_url
        )

        if not video_id:

            st.error(
                "Invalid YouTube URL. "
                "Please enter a valid YouTube video URL."
            )

        else:

            with st.spinner(
                "Fetching YouTube transcript..."
            ):

                transcript = get_transcript(
                    video_id
                )


            # ----------------------------------------------
            # Check transcript result
            # ----------------------------------------------

            if transcript.startswith("ERROR:"):

                st.error(
                    transcript
                )

            else:

                st.session_state.transcript = transcript

                st.session_state.video_id = video_id

                # Clear previous chat for new video
                st.session_state.messages = []

                st.success(
                    "✅ Transcript extracted successfully!"
                )


# ============================================================
# Display YouTube Video
# ============================================================

if st.session_state.video_id:

    st.subheader("🎬 Video")

    video_url = (
        "https://www.youtube.com/watch?v="
        + st.session_state.video_id
    )

    st.video(video_url)


# ============================================================
# Display Transcript
# ============================================================

if st.session_state.transcript:

    st.subheader("📝 Video Transcript")

    with st.expander(
        "Click here to view the complete transcript"
    ):

        st.write(
            st.session_state.transcript
        )


    # ========================================================
    # Chat Section
    # ========================================================

    st.subheader(
        "💬 Ask Questions About the Video"
    )


    # ========================================================
    # Display Chat History
    # ========================================================

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # ========================================================
    # User Question
    # ========================================================

    question = st.chat_input(
        "Ask something about the video..."
    )


    # ========================================================
    # Process Question
    # ========================================================

    if question:

        # ----------------------------------------------------
        # Display User Question
        # ----------------------------------------------------

        with st.chat_message("user"):

            st.write(
                question
            )


        # ----------------------------------------------------
        # Save User Question
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # ----------------------------------------------------
        # Generate Gemini Response
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "🤖 Gemini is analyzing the video..."
            ):

                try:

                    answer = ask_gemini(
                        st.session_state.transcript,
                        question
                    )


                    # Display answer

                    st.write(
                        answer
                    )


                    # Save answer

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )


                except Exception as e:

                    st.error(
                        f"Error while generating response: {str(e)}"
                    )


# ============================================================
# No Video Loaded
# ============================================================

else:

    st.info(
        "👆 Enter a YouTube URL above and click "
        "'Process Video' to get started."
    )


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "🎥 YouTube Video Q&A • Powered by Google Gemini"
)