from pathlib import Path

PROCESSED_DIR = Path("data/processed")
UPLOAD_DIR = Path("data/uploads")


def get_project_summary(project_id: str) -> dict:
    project_processed_dir = PROCESSED_DIR / project_id
    project_upload_dir = UPLOAD_DIR / project_id

    uploaded_files = []
    chunk_files = []

    if project_upload_dir.exists():
        uploaded_files = list(project_upload_dir.glob("*"))

    if project_processed_dir.exists():
        chunk_files = list(project_processed_dir.glob("*_chunks.txt"))

    total_chunks = 0

    for chunk_file in chunk_files:
        content = chunk_file.read_text(encoding="utf-8")
        total_chunks += content.count("---CHUNK")

    return {
        "project_id": project_id,
        "total_documents": len(uploaded_files),
        "total_chunk_files": len(chunk_files),
        "total_chunks": total_chunks,
        "uploaded_documents": [file.name for file in uploaded_files],
        "processed_files": [file.name for file in chunk_files],
        "available_features": [
            "chat",
            "risk-summary",
            "generate-report"
        ],
        "status": "ready" if total_chunks > 0 else "no_documents_found"
    }