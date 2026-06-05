from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.document_service import save_uploaded_file, extract_pdf_text
from app.services.rag_service import (
    store_document_chunks,
    answer_project_question,
    chunk_text,
    embed_text
)
from app.services.vector_db_service import save_document_with_chunks
from app.services.classification_service import classify_construction_document
from app.services.risk_service import generate_project_risk_summary
from app.services.report_service import generate_project_report
from app.services.project_service import get_project_summary
from app.services.search_service import search_project_documents
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    RiskSummaryRequest,
    ReportRequest,
    SearchRequest
)

router = APIRouter()
router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = Form("demo-project"),
    document_type: str = Form("auto"),
    db: Session = Depends(get_db)
):
    file_path = save_uploaded_file(file, project_id)
    extracted_text = extract_pdf_text(file_path)

    # Existing file-based storage
    chunks_created = store_document_chunks(
        project_id=project_id,
        filename=file.filename,
        text=extracted_text
    )

    # New DB-backed storage
    chunks = chunk_text(extracted_text)
    embeddings = [embed_text(chunk) for chunk in chunks]

    classification = classify_construction_document(extracted_text)

    detected_document_type = classification.get(
        "document_type",
        document_type
    )

    db_document = save_document_with_chunks(
        db=db,
        project_id=project_id,
        filename=file.filename,
        document_type=detected_document_type,
        chunks=chunks,
        embeddings=embeddings
    )

    return {
        "project_id": project_id,
        "filename": file.filename,
        "characters_extracted": len(extracted_text),
        "chunks_created": chunks_created,
        "db_document_id": db_document.id,
        "stored_in_postgres": True,
        "classification": classification,
        "message": "Document uploaded, embedded, classified, and stored in PostgreSQL successfully."
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_project_docs(request: ChatRequest):
    result = answer_project_question(
        project_id=request.project_id,
        question=request.question
    )

    return ChatResponse(
        answer=result["answer"],
        citations=result["citations"]
    )


@router.post("/risk-summary")
async def risk_summary(request: RiskSummaryRequest):
    summary = generate_project_risk_summary(request.project_id)

    return {
        "project_id": request.project_id,
        "risk_summary": summary
    }
@router.post("/generate-report")
async def generate_report(request: ReportRequest):
    report = generate_project_report(request.project_id)

    return {
        "project_id": request.project_id,
        "report": report
    }
@router.get("/project-summary/{project_id}")
async def project_summary(project_id: str):
    return get_project_summary(project_id)

@router.post("/search-documents")
async def search_documents(request: SearchRequest):
    return {
        "project_id": request.project_id,
        "search": search_project_documents(
            project_id=request.project_id,
            query=request.query,
            top_k=request.top_k
        )
    }
@router.post("/db-chat", response_model=ChatResponse)
async def db_chat_with_project_docs(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    result = answer_question_from_db(
        db=db,
        project_id=request.project_id,
        question=request.question
    )

    return ChatResponse(
        answer=result["answer"],
        citations=result["citations"]
    )