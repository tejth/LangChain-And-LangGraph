from crewai import Crew, Process

from agents import news_researcher, news_writer
from tasks import research_task, write_task


# ============================================================
# Create the Crew
# ============================================================

crew = Crew(
    agents=[
        news_researcher,
        news_writer
    ],

    tasks=[
        research_task,
        write_task
    ],

    process=Process.sequential,

    verbose=True
)