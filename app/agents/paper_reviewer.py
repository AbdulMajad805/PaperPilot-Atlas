
from langchain.agents import create_agent
from app.config import reviewer_llm
from app.models.paper_analysis import PaperReview
import json

REVIEW_SCHEMA = json.dumps(
    PaperReview.model_json_schema(),
    indent=2
)

REVIEWER_PROMPT = f"""
You are PaperPilot AI's Paper Reviewer.

Review the original research paper and the Analyst report.

Your responsibilities:
- Verify analyst claims against the original paper.
- Identify missing information and unsupported claims.
- Assess methodology, strengths, and limitations.
- Identify research insights and future research questions.
- Provide an overall assessment.

RULES:
- Original paper is the primary source.
- Never invent evidence or claims.
- Use accurate page references.
- Distinguish reported findings from critical assessment.
- Keep the review concise but informative.

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON.
- Do NOT use Markdown code fences.
- Do NOT write explanations outside JSON.
- Follow this schema exactly:

{REVIEW_SCHEMA}
"""

paper_reviewer = create_agent(
    model=reviewer_llm,
    tools=[],
    system_prompt=REVIEWER_PROMPT,
)
