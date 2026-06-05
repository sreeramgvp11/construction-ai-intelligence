from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from app.services.llm_service import generate_answer
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


def embed_text(text: str):
    return model.encode(text)


def store_document_chunks(project_id: str, filename: str, text: str):
    chunks = chunk_text(text)

    project_dir = PROCESSED_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    chunks_path = project_dir / f"{filename}_chunks.txt"
    embeddings_path = project_dir / f"{filename}_embeddings.npy"

    embeddings = []

    with chunks_path.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"---CHUNK {i}---\n")
            f.write(chunk + "\n")

            embeddings.append(embed_text(chunk))

    np.save(embeddings_path, np.array(embeddings))

    return len(chunks)


def load_chunks(project_id: str):
    project_dir = PROCESSED_DIR / project_id

    all_chunks = []
    all_embeddings = []
    all_metadata = []

    if not project_dir.exists():
        return [], np.array([]), []

    for chunks_file in project_dir.glob("*_chunks.txt"):
        embeddings_file = project_dir / chunks_file.name.replace("_chunks.txt", "_embeddings.npy")

        if not embeddings_file.exists():
            continue

        filename = chunks_file.name.replace("_chunks.txt", "")

        content = chunks_file.read_text(encoding="utf-8")
        raw_chunks = content.split("---CHUNK ")

        chunks = []
        metadata = []

        for raw in raw_chunks:
            if "---" in raw:
                chunk_header, chunk_text_part = raw.split("---", 1)
                chunk_id = int(chunk_header.strip())

                chunks.append(chunk_text_part.strip())
                metadata.append({
                    "source_id": f"{filename}::chunk_{chunk_id}",
                    "filename": filename,
                    "chunk_id": chunk_id
                })

        embeddings = np.load(embeddings_file)

        all_chunks.extend(chunks)
        all_embeddings.extend(embeddings)
        all_metadata.extend(metadata)

    return all_chunks, np.array(all_embeddings), all_metadata


def retrieve_relevant_chunks(project_id: str, question: str, top_k: int = 3):
    chunks, embeddings, metadata = load_chunks(project_id)

    if len(chunks) == 0:
        return []

    question_embedding = embed_text(question)

    similarities = embeddings @ question_embedding / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(question_embedding)
    )

    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []

    for i in top_indices:
        results.append({
            "content": chunks[i],
            "score": float(similarities[i]),
            "source_id": metadata[i]["source_id"],
            "filename": metadata[i]["filename"],
            "chunk_id": metadata[i]["chunk_id"]
        })

    return results


def answer_project_question(project_id: str, question: str) -> dict:
    results = retrieve_relevant_chunks(
        project_id=project_id,
        question=question,
        top_k=3
    )

    if not results:
        return {
            "answer": "No documents found.",
            "citations": []
        }

    context = "\n\n".join(
        [
            f"[Source {i+1}: {item['source_id']}]\n{item['content']}"
            for i, item in enumerate(results)
        ]
    )

    prompt = f"""
You are an AI assistant for construction project managers.

Use only the provided context.
If the answer is not present in the context, say the uploaded documents do not contain enough information.

Context:
{context}

Question:
{question}

Write a clear answer for a construction project manager.
Mention source labels such as [Source 1], [Source 2] when using information.
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