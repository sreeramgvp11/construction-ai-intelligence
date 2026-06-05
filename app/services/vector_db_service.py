from sqlalchemy.orm import Session
from app.db.models import Project, Document, DocumentChunk


def get_or_create_project(db: Session, project_id: str):
    project = db.query(Project).filter(Project.project_id == project_id).first()

    if project:
        return project

    project = Project(project_id=project_id)
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def save_document_with_chunks(
    db: Session,
    project_id: str,
    filename: str,
    document_type: str,
    chunks: list[str],
    embeddings: list
):
    project = get_or_create_project(db, project_id)

    document = Document(
        filename=filename,
        document_type=document_type,
        project_id=project.id
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    for index, chunk in enumerate(chunks):
        embedding = embeddings[index]

        db_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding.tolist() if hasattr(embedding, "tolist") else embedding
        )

        db.add(db_chunk)

    db.commit()

    return document