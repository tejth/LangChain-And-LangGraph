import os

from dotenv import load_dotenv
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import tool

load_dotenv()


# ============================================================
# Google Gemini Configuration
# ============================================================

google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError(
        "GOOGLE_API_KEY is missing from the .env file."
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    google_api_key=google_api_key
)


# ============================================================
# Researcher Agent
# ============================================================

news_researcher = Agent(
    role="Senior Technology Researcher",

    goal=(
        "Research and identify the latest important "
        "developments, trends, opportunities and risks "
        "related to {topic}."
    ),

    backstory=(
        "You are an experienced technology researcher "
        "who specializes in discovering emerging "
        "technologies and analyzing their impact on "
        "industries and society."
    ),

    verbose=True,

    memory=True,

    tools=[tool],

    llm=llm,

    allow_delegation=True
)


# ============================================================
# Writer Agent
# ============================================================

news_writer = Agent(
    role="Technology Content Writer",

    goal=(
        "Write an engaging, informative and easy-to-understand "
        "article about {topic} using the research provided."
    ),

    backstory=(
        "You are a professional technology writer who is "
        "skilled at turning complex technical information "
        "into simple and engaging articles."
    ),

    verbose=True,

    memory=True,

    tools=[tool],

    llm=llm,

    allow_delegation=False
)