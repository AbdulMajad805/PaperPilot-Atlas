
import json
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.paper_analyst import paper_analyst
from app.agents.paper_reviewer import paper_reviewer
from app.models.paper_analysis import PaperAnalysis, PaperReview


class PaperPilotState(TypedDict):
    paper_text: str
    analysis: str
    review: str


def extract_json(text: str) -> str:
    """Extract JSON from a model response."""
    text = text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0].strip()

    return text


def analyst_node(state: PaperPilotState):
    result = paper_analyst.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
Analyze this research paper.

Return ONLY valid JSON matching this structure:
{json.dumps(PaperAnalysis.model_json_schema(), indent=2)}

PAPER:
{state['paper_text']}
"""
            }
        ]
    })

    message = result["messages"][-1]
    response=  message.content

    print("\n========== GROQ GENERATION DETAILS ==========")
    print("Finish reason:", message.response_metadata.get("finish_reason"))
    print("Token usage:", message.usage_metadata)
    print("Response characters:", len(message.content))
    print("==========================================")

    
    response = extract_json(response)


    print("\n========== ANALYST RESPONSE DEBUG ==========")
    print("Response length:", len(response))
    print("Response ending:")
    print(response[-500:])
    print("==========================================")

    # Validate model output using Pydantic
    analysis = PaperAnalysis.model_validate_json(response)

    return {"analysis": analysis.model_dump_json(indent=2)}


def reviewer_node(state: PaperPilotState):
    result = paper_reviewer.invoke({
    "messages": [
        {
            "role": "user",
            "content": f"""
Review the Analyst report against the original research paper.

ORIGINAL PAPER:
{state['paper_text'][:6000]}

ANALYST REPORT:
{state['analysis']}

Verify claims using the available source evidence.
Identify unsupported claims, missing information,
methodological issues, strengths, limitations,
and research questions.

Keep the review concise and evidence-based.
"""
        }
        ]
    })

    response = result["messages"][-1].content
    response = extract_json(response)

    # Validate model output using Pydantic
    review = PaperReview.model_validate_json(response)

    return {"review": review.model_dump_json(indent=2)}


builder = StateGraph(PaperPilotState)

builder.add_node("analyst", analyst_node)
builder.add_node("reviewer", reviewer_node)

builder.add_edge(START, "analyst")
builder.add_edge("analyst", "reviewer")
builder.add_edge("reviewer", END)

paperpilot_workflow = builder.compile()
