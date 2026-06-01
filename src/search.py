from src.embedder import get_embedding
from src.vector_store import get_collection, search


def semantic_search(query: str, n_results: int = 5, category_filter: str | None = None) -> list[dict]:
    """
    Run semantic search against the TechFlow knowledge base.
    Returns list of results with text, metadata, and similarity score.
    """
    collection = get_collection()
    query_embedding = get_embedding(query)
    raw_results = search(collection, query_embedding, n_results, category_filter)

    results = []
    for i in range(len(raw_results["ids"][0])):
        results.append({
            "rank": i + 1,
            "text": raw_results["documents"][0][i],
            "category": raw_results["metadatas"][0][i]["category"],
            "source": raw_results["metadatas"][0][i]["source"],
            "distance": round(raw_results["distances"][0][i], 4)
        })
    return results