from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    project_id: str
    question: str


class Citation(BaseModel):
    source_id: str
    filename: str
    chunk_id: int
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]


class RiskSummaryRequest(BaseModel):
    project_id: str


class ReportRequest(BaseModel):
    project_id: str


class SearchRequest(BaseModel):
    project_id: str
    query: str
    top_k: int = 5