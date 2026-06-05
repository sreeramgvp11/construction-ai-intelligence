# Future database models:
# Project
# Document
# DocumentChunk
# ChatSession
# AnalysisReport

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    project_id = Column(String, unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    documents = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    filename = Column(String, nullable=False)

    document_type = Column(String)

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    project = relationship(
        "Project",
        back_populates="documents"
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id")
    )

    chunk_index = Column(Integer)

    content = Column(Text)

    embedding = Column(Vector(384))

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    document = relationship(
        "Document",
        back_populates="chunks"
    )
