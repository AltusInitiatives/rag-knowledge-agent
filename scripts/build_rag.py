import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chunker import chunk_documents
from src.embedder import get_embeddings_batch
from src.vector_store import get_collection
import chromadb


def main():
    with open("data/documents.json") as f:
        documents = json.load(f)

    print(f"Loaded {len(documents)} source documents.")

    chunks = chunk_documents(documents, chunk_size=500, overlap=100)
    print(f"Generated {len(chunks)} chunks.")

    # Use a separate collection for RAG (keeps Day 43 collection intact)
    db = chromadb.PersistentClient(path=".chroma")
    try:
        db.delete_collection("techflow_rag")
    except Exception:
        pass

    collection = db.get_or_create_collection(
        name="techflow_rag",
        metadata={"hnsw:space": "cosine"}
    )

    texts = [c["text"] for c in chunks]
    print("Generating embeddings for chunks...")
    embeddings = get_embeddings_batch(texts)

    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "category": c["category"],
            "source": c["source"],
            "parent_id": c["parent_id"]
        } for c in chunks]
    )

    print(f"RAG collection built. {collection.count()} chunks indexed.")


if __name__ == "__main__":
    main()