import json
from pathlib import Path
from src.hybrid_retriever import hybrid_search
from src.reranker import rerank
from src.query_transformer import transform_query
from src.rag import generate


def load_documents(path: str = "data/documents.json") -> list[dict]:
    with open(path) as f:
        return json.load(f)


def ask_enhanced(
    query: str,
    use_query_transform: bool = True,
    use_reranking: bool = True,
    n_retrieve: int = 8,
    n_rerank: int = 3
) -> dict:
    """
    Enhanced RAG pipeline:
    1. Optionally transform the query
    2. Hybrid search (vector + BM25)
    3. Optionally rerank retrieved chunks
    4. Generate answer from top chunks
    """
    documents = load_documents()

    # Step 1: Query transformation
    transformed_query = transform_query(query) if use_query_transform else query

    # Step 2: Hybrid retrieval
    chunks = hybrid_search(
        query=transformed_query,
        all_documents=documents,
        n_results=n_retrieve
    )

    # Step 3: Reranking
    if use_reranking:
        chunks = rerank(transformed_query, chunks, top_n=n_rerank)
    else:
        chunks = chunks[:n_rerank]

    # Step 4: Generate
    answer = generate(transformed_query, chunks)

    return {
        "original_query": query,
        "transformed_query": transformed_query,
        "answer": answer,
        "chunks_used": len(chunks),
        "sources": [{"source": c["source"], "category": c["category"]} for c in chunks]
    }