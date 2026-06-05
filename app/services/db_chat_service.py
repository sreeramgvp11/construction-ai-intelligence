from sqlalchemy.orm import Session
from app.services.db_search_service import search_chunks_from_db
from app.services.llm_service import generate_answer


def answer_question_from_db(
    db: Session,
    project_id: str,
    question: str,
    top_k: int = 3
):
    results = search_chunks_from_db(
        db=db,
        project_id=project_id,
        query=question,
        top_k=top_k
    )

    if not results:
        return {
            "answer": "No documents found for this project.",
            "citations": []
        }

    context = "\n\n".join(
        [
            f"[Source {i + 1}: {item['source_id']}]\n{item['content']}"
            for i, item in enumerate(results)
        ]
    )

    prompt = f"""
You are an AI assistant for construction project managers.

Use only the provided project document context.
If the answer is not found in the context, say the uploaded documents do not contain enough information.

Context:
{context}

Question:
{question}

Provide:
1. Direct answer
2. Key findings
3. Sources used using the exact source labels
"""

    answer = generate_answer(prompt)

    citations = [
        {
            "source_id": item["source_id"],
            "filename": item["filename"],
            "chunk_id": item["chunk_id"],
            "score": item["score"]
        }
        for item in results
    ]

    return {
        "answer": answer,
        "citations": citations
    }