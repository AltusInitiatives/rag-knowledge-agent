import chromadb
from chromadb.config import Settings


def get_collection(collection_name: str = "techflow_docs", persist_dir: str = ".chroma"):
    """Get or create a Chroma collection with persistence."""
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # cosine similarity
    )
    return collection


def add_documents(collection, documents: list[dict], embeddings: list[list[float]]) -> None:
    """Add documents with their embeddings to the collection."""
    collection.add(
        ids=[doc["id"] for doc in documents],
        embeddings=embeddings,
        documents=[doc["text"] for doc in documents],
        metadatas=[{
            "category": doc["category"],
            "source": doc["source"],
            "date": doc["date"]
        } for doc in documents]
    )
    print(f"Added {len(documents)} documents to collection.")


def search(collection, query_embedding: list[float], n_results: int = 5, category_filter: str | None = None) -> dict:
    """Search the collection for similar documents."""
    where_clause = {"category": category_filter} if category_filter else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_clause,
        include=["documents", "metadatas", "distances"]
    )
    return results