from langchain.agents import create_agent
from app.config import analyst_llm
from app.models.paper_analysis import PaperAnalysis

ANALYST_PROMPT = """
You are PaperPilot AI's Paper Analyst.

Analyze the supplied research paper using ONLY its content.

Extract:
- Paper metadata
- Research problem
- Objectives
- Methodology
- Architecture
- Experimental setup
- Datasets
- Results
- Contributions
- Limitations
- Executive summary

Rules:
- Never invent information.
- Use "Not specified" when information is unavailable.
- Include accurate PDF page references.
- Preserve technical terminology.
- Distinguish paper-reported results from interpretation.
"""

paper_analyst = create_agent(
    model=analyst_llm,
    tools=[],
    system_prompt=ANALYST_PROMPT,
)