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
            "report_title": "Construction Project Intelligence Report",
            "executive_summary": text[:1000],
            "documents_reviewed": [],
            "major_risks": [],
            "cost_impact": "Unknown",
            "schedule_impact": "Unknown",
            "technical_issues": [],
            "recommended_actions": [],
            "final_assessment": "Unable to generate structured JSON report."
        }

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {
            "report_title": "Construction Project Intelligence Report",
            "executive_summary": text[:1000],
            "documents_reviewed": [],
            "major_risks": [],
            "cost_impact": "Unknown",
            "schedule_impact": "Unknown",
            "technical_issues": [],
            "recommended_actions": [],
            "final_assessment": "Unable to parse structured report."
        }


def generate_project_report(project_id: str) -> dict:
    chunks, _, _ = load_chunks(project_id)

    if not chunks:
        return {
            "report_title": "Construction Project Intelligence Report",
            "executive_summary": "No project documents found. Please upload documents first.",
            "documents_reviewed": [],
            "major_risks": [],
            "cost_impact": "Unknown",
            "schedule_impact": "Unknown",
            "technical_issues": [],
            "recommended_actions": [],
            "final_assessment": "No report generated."
        }

    context = "\n\n".join(chunks[:10])

    prompt = f"""
You are an AI construction project analyst.

Generate a professional project intelligence report based on the provided construction documents.

Return ONLY valid JSON in this exact format:

{{
  "report_title": "Construction Project Intelligence Report",
  "executive_summary": "...",
  "documents_reviewed": ["...", "..."],
  "major_risks": ["...", "..."],
  "cost_impact": "...",
  "schedule_impact": "...",
  "technical_issues": ["...", "..."],
  "safety_issues": ["...", "..."],
  "missing_information": ["...", "..."],
  "recommended_actions": ["...", "..."],
  "final_assessment": "..."
}}

Project document context:
{context}
"""

    response = generate_answer(prompt)
    return _extract_json(response)