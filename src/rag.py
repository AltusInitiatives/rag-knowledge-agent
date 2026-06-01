from openai import OpenAI
from dotenv import load_dotenv
from src.embedder import get_embedding
from src.vector_store import get_collection

load_dotenv()
client = OpenAI()


def retrieve(query: str, collection_name: str = "techflow_rag", n_results: int = 5) -> list[dict]:
    """Retrieve the top-n most relevant chunks for a query."""
    collection = get_collection(collection_name)
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    return [
        {
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "category": results["metadatas"][0][i]["category"],
            "distance": round(results["distances"][0][i], 4)
        }
        for i in range(len(results["ids"][0]))
    ]


def generate(query: str, chunks: list[dict], model: str = "gpt-4o-mini") -> str:
    """Generate an answer grounded in the retrieved chunks."""
    context = "\n\n".join([
        f"[Source: {c['source']} | Category: {c['category']}]\n{c['text']}"
        for c in chunks
    ])

    system_prompt = """You are a helpful support assistant for TechFlow.
Answer the user's question using ONLY the information in the provided context.
Always cite your source using the format [Source: X].
If the context does not contain enough information to answer, say so clearly — do not guess."""

    user_message = f"""Context:
{context}

Question: {query}"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0
    )
    return response.choices[0].message.content


def ask(query: str, collection_name: str = "techflow_rag", n_results: int = 5) -> dict:
    """Full RAG pipeline: retrieve + generate."""
    chunks = retrieve(query, collection_name, n_results)
    answer = generate(query, chunks)
    return {
        "query": query,
        "answer": answer,
        "sources_used": [{"source": c["source"], "category": c["category"], "distance": c["distance"]} for c in chunks]
    }