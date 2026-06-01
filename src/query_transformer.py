from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def transform_query(query: str) -> str:
    """
    Rewrite a user query to improve semantic search recall.
    Expands vague terms, adds context, and removes filler.
    Returns the rewritten query — or the original if it's already clear.
    """
    prompt = f"""You are a search query optimizer for a software product knowledge base.

Rewrite the following user query to improve semantic search results. Your rewrite should:
- Expand abbreviations and vague terms
- Add relevant synonyms if helpful
- Make implicit intent explicit
- Keep it concise (under 30 words)
- If the query is already clear and specific, return it unchanged

Original query: {query}

Respond ONLY with the rewritten query. No explanation, no quotes."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()