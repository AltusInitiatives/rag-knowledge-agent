import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embedder import get_embeddings_batch
from src.vector_store import get_collection, add_documents


def main():
    with open("data/documents.json") as f:
        documents = json.load(f)

    print(f"Loaded {len(documents)} documents.")

    # Batch embed all documents in one API call
    texts = [doc["text"] for doc in documents]
    print("Generating embeddings...")
    embeddings = get_embeddings_batch(texts)

    collection = get_collection()
    
    # Clear existing data if re-ingesting
    existing = collection.count()
    if existing > 0:
        print(f"Clearing {existing} existing documents...")
        collection.delete(where={"category": {"$ne": ""}})  # delete all

    add_documents(collection, documents, embeddings)
    print(f"Ingestion complete. Collection now has {collection.count()} documents.")


if __name__ == "__main__":
    main()