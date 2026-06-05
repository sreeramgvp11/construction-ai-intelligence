import json
import re
from app.services.llm_service import generate_answer

def fallback_classify_document(text: str) -> dict:
    lower_text = text.lower()

    document_type = "General"
    discipline = "General"
    risk_level = "Unknown"

    if "request for information" in lower_text or "rfi" in lower_text:
        document_type = "RFI"
    elif "change order" in lower_text:
        document_type = "Change Order"
    elif "safety" in lower_text:
        document_type = "Safety Report"
    elif "inspection" in lower_text:
        document_type = "Inspection Report"
    elif "contract" in lower_text:
        document_type = "Contract"

    if "hvac" in lower_text or "mechanical" in lower_text:
        discipline = "Mechanical"
    elif "electrical" in lower_text:
        discipline = "Electrical"
    elif "plumbing" in lower_text:
        discipline = "Plumbing"
    elif "structural" in lower_text or "beam" in lower_text:
        discipline = "Structural"

    if "delay" in lower_text or "cost" in lower_text or "conflict" in lower_text:
        risk_level = "High"
    elif "approval" in lower_text:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "document_type": document_type,
        "discipline": discipline,
        "risk_level": risk_level,
        "summary": text[:500],
        "important_items": [],
        "cost_impact": "Detected from document" if "cost" in lower_text else "Unknown",
        "schedule_impact": "Detected from document" if "delay" in lower_text else "Unknown",
        "recommended_action": "Review document and resolve identified issues."
    }

def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {
            "document_type": "Unknown",
            "discipline": "Unknown",
            "risk_level": "Unknown",
            "summary": text[:500],
            "important_items": []
        }

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {
            "document_type": "Unknown",
            "discipline": "Unknown",
            "risk_level": "Unknown",
            "summary": text[:500],
            "important_items": []
        }


def classify_construction_document(text: str) -> dict:
    sample_text = text[:6000]

    prompt = f"""
You are an AI assistant for construction project document intelligence.

Classify the following construction document.

Allowed document_type values:
- Contract
- RFI
- Change Order
- Site Report
- Inspection Report
- Safety Report
- Blueprint
- General

Allowed discipline values:
- Electrical
- Mechanical
- Plumbing
- Structural
- Civil
- Architectural
- Safety
- General

Allowed risk_level values:
- Low
- Medium
- High
- Unknown

Return ONLY valid JSON in this exact format:

{{
  "document_type": "...",
  "discipline": "...",
  "risk_level": "...",
  "summary": "...",
  "important_items": ["...", "..."],
  "cost_impact": "...",
  "schedule_impact": "...",
  "recommended_action": "..."
}}

Document text:
{sample_text}
"""

    response = generate_answer(prompt)

    if (
        "LLM service temporarily unavailable" in response
        or "RESOURCE_EXHAUSTED" in response
        or "quota" in response.lower()
        or "unavailable" in response.lower()
    ):
        return fallback_classify_document(text)

    return _extract_json(response)