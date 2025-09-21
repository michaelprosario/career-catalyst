import os
import sys

import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

current = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent)

from job_search_infra import job_search_services


def job_search_for_agent(city: str, search_term: str) -> dict:
    city = city.strip()
    search_term = search_term.strip()
    jobs_data_frame = job_search_services.job_search(search_term=search_term, location=city, results_wanted=20)
    markdown_jobs = job_search_services.get_job_list_markdown(jobs_data_frame)
    return {
        "status": "success",
        "report": markdown_jobs
    }


root_agent = Agent(
    name="job_search_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about job searching."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about job searching.  As you return information to the user with job listing, make sure to include the job title, job url, and company"
    ),
    tools=[job_search_for_agent],
)

