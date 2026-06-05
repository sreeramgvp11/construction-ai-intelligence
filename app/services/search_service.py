from app.services.rag_service import retrieve_relevant_chunks


def search_project_documents(project_id: str, query: str, top_k: int = 5):
    results = retrieve_relevant_chunks(
        project_id=project_id,
        question=query,
        top_k=top_k
    )

    return {
        "query": query,
        "total_results": len(results),
        "results": results
    }