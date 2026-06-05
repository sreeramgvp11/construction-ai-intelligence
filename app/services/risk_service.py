import json
import re
from app.services.rag_service import load_chunks
from app.services.llm_service import generate_answer


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return {
            "overall_risk": "Unknown",
            "cost_risks": [],
            "schedule_risks": [],
            "technical_risks": [],
            "safety_risks": [],
            "recommended_actions": [],
            "summary": text[:700]
        }

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {
            "overall_risk": "Unknown",
            "cost_risks": [],
            "schedule_risks": [],
            "technical_risks": [],
            "safety_risks": [],
            "recommended_actions": [],
            "summary": text[:700]
        }


def generate_project_risk_summary(project_id: str) -> dict:
    chunks, _, _ = load_chunks(project_id)

    if not chunks:
        return {
            "overall_risk": "Unknown",
            "cost_risks": [],
            "schedule_risks": [],
            "technical_risks": [],
            "safety_risks": [],
            "recommended_actions": [],
            "summary": "No project documents found. Please upload documents first."
        }

    context = "\n\n".join(chunks[:8])

    prompt = f"""
You are a construction project risk analyst.

Analyze the following construction project documents and generate a structured risk summary.

Focus on:
- Cost risk
- Schedule delay risk
- Technical coordination risk
- Safety risk
- Missing approvals
- Required next actions

Return ONLY valid JSON in this exact format:

{{
  "overall_risk": "Low | Medium | High | Unknown",
  "cost_risks": ["...", "..."],
  "schedule_risks": ["...", "..."],
  "technical_risks": ["...", "..."],
  "safety_risks": ["...", "..."],
  "missing_information": ["...", "..."],
  "recommended_actions": ["...", "..."],
  "executive_summary": "..."
}}

Project document context:
{context}
"""

    response = generate_answer(prompt)
    return _extract_json(response)