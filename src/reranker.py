from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def rerank(query: str, chunks: list[dict], top_n: int = 3) -> list[dict]:
    """
    Use the LLM to score each chunk's relevance to the query.
    Returns top_n chunks sorted by relevance score descending.
    """
    if not chunks:
        return []

    chunks_text = "\n\n".join([
        f"[Chunk {i+1}]\n{c['text']}"
        for i, c in enumerate(chunks)
    ])

    prompt = f"""You are a relevance scoring system.

Query: {query}

Below are {len(chunks)} retrieved text chunks. Score each chunk's relevance to the query on a scale of 0-10, where:
- 10 = directly and completely answers the query
- 7-9 = highly relevant, contains most of the answer
- 4-6 = partially relevant, tangentially related
- 1-3 = loosely related
- 0 = not relevant

{chunks_text}

Respond ONLY with a JSON array of scores in order, e.g.: [8, 3, 9, 1, 5]
No explanation, just the array."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    import json
    try:
        scores = json.loads(response.choices[0].message.content.strip())
    except Exception:
        # Fallback: return original order if parsing fails
        return chunks[:top_n]

    scored = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [chunk for chunk, _ in scored[:top_n]]