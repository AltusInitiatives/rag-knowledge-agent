import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from src.embedder import get_embeddings_batch, get_embedding


def build_collection(client, name: str, model: str, documents: list[dict]) -> chromadb.Collection:
    """Create (or recreate) a collection and ingest all documents with the given model."""
    # Delete existing collection if present
    try:
        client.delete_collection(name)
        print(f"Cleared existing collection: {name}")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )

    texts = [doc["text"] for doc in documents]
    print(f"Generating embeddings with {model}...")
    embeddings = get_embeddings_batch(texts, model=model)

    collection.add(
        ids=[doc["id"] for doc in documents],
        embeddings=embeddings,
        documents=[doc["text"] for doc in documents],
        metadatas=[{"category": doc["category"]} for doc in documents]
    )
    print(f"Ingested {len(documents)} docs into '{name}'.")
    return collection


def search_collection(collection, query: str, model: str, n_results: int = 3) -> list[dict]:
    embedding = get_embedding(query, model=model)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "distances"]
    )
    return [
        {
            "text": results["documents"][0][i][:100],
            "distance": round(results["distances"][0][i], 4)
        }
        for i in range(len(results["ids"][0]))
    ]


COMPARISON_QUERIES = [
    "How do I integrate with third-party tools?",
    "What is the cancellation policy?",
    "I can't log in to my account",
    "How does pricing scale with team size?",
    "What data does TechFlow store about me?",
    "How do I set up automated workflows?",
    "Can I customize notification settings?",
    "What happens to my data if I cancel?",
    "How do I upgrade my plan?",
    "Does TechFlow support SSO?"
]


def main():
    with open("data/documents.json") as f:
        documents = json.load(f)

    client = chromadb.PersistentClient(path=".chroma")

    # Build one collection per model
    small_col = build_collection(client, "techflow_small", "text-embedding-3-small", documents)
    time.sleep(1)
    large_col = build_collection(client, "techflow_large", "text-embedding-3-large", documents)

    # Run comparison
    lines = [
        "# Embedding Model Comparison: small vs large\n",
        "| Query | Small Top-1 Distance | Large Top-1 Distance | Same Top Result? |",
        "|-------|---------------------|---------------------|-----------------|"
    ]

    for query in COMPARISON_QUERIES:
        small = search_collection(small_col, query, "text-embedding-3-small")
        large = search_collection(large_col, query, "text-embedding-3-large")
        same = "✅" if small[0]["text"] == large[0]["text"] else "❌"
        lines.append(
            f"| {query[:50]} | {small[0]['distance']} | {large[0]['distance']} | {same} |"
        )
        print(f"Compared: {query[:50]}")
        time.sleep(0.3)

    lines += [
        "\n## Cost Reference",
        "- text-embedding-3-small: $0.02 / 1M tokens",
        "- text-embedding-3-large: $0.13 / 1M tokens (6.5x more expensive)",
        "\n## Conclusion",
        "Add your analysis here: Did large produce meaningfully better results (lower distances, different top results)? Was the quality delta worth 6.5x the cost for this use case?"
    ]

    Path("results").mkdir(exist_ok=True)
    with open("results/model_comparison.md", "w") as f:
        f.write("\n".join(lines))

    print("\nComparison saved to results/model_comparison.md")


if __name__ == "__main__":
    main()