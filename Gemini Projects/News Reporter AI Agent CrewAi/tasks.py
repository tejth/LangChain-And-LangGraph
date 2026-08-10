from crewai import Task

from agents import news_researcher, news_writer
from tools import tool


# ============================================================
# Research Task
# ============================================================

research_task = Task(
    description=(
        "Research the latest developments and trends in {topic}. "
        "Identify the most important recent developments. "
        "Focus on the major advantages, disadvantages, "
        "market opportunities, industry impact and potential risks. "
        "Use reliable and recent web information."
    ),

    expected_output=(
        "A comprehensive three-paragraph research report about "
        "{topic}. The report should include the latest trends, "
        "key developments, advantages, disadvantages, market "
        "opportunities and potential risks."
    ),

    tools=[tool],

    agent=news_researcher
)


# ============================================================
# Writing Task
# ============================================================

write_task = Task(
    description=(
        "Using the research produced by the researcher, "
        "write an insightful article about {topic}. "
        "Explain the latest developments and their impact "
        "on the industry. Make the article informative, "
        "engaging, positive and easy to understand."
    ),

    expected_output=(
        "A well-structured four-paragraph article about "
        "{topic}, formatted in Markdown."
    ),

    tools=[tool],

    agent=news_writer,

    async_execution=False,

    output_file="new-blog-post.md"
)