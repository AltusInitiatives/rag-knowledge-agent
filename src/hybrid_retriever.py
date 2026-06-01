import math
import re
from collections import Counter
from src.embedder import get_embedding
from src.vector_store import get_collection


def tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, remove punctuation, split on whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()


class BM25:
    """
    Minimal BM25 implementation for keyword scoring.
    BM25 rewards term frequency in a document while penalizing
    very long documents — better than raw word count matching.
    """
    def __init__(self, documents: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents = documents
        self.tokenized = [tokenize(d) for d in documents]
        self.doc_lengths = [len(t) for t in self.tokenized]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)
        self.df = self._compute_df()
        self.n = len(documents)

    def _compute_df(self) -> dict[str, int]:
        df: dict[str, int] = {}
        for tokens in self.tokenized:
            for token in set(tokens):
                df[token] = df.get(token, 0) + 1
        return df

    def score(self, query: str, doc_index: int) -> float:
        tokens = tokenize(query)
        doc_tokens = self.tokenized[doc_index]
        doc_len = self.doc_lengths[doc_index]
        tf_counts = Counter(doc_tokens)
        score = 0.0
        for token in tokens:
            if token not in self.df:
                continue
            tf = tf_counts.get(token, 0)
            idf = math.log((self.n - self.df[token] + 0.5) / (self.df[token] + 0.5) + 1)
            tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_length))
            score += idf * tf_norm
        return score

    def get_top_n(self, query: str, n: int = 5) -> list[tuple[int, float]]:
        scores = [(i, self.score(query, i)) for i in range(self.n)]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:n]


def hybrid_search(
    query: str,
    all_documents: list[dict],
    collection_name: str = "techflow_rag",
    n_results: int = 5,
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3
) -> list[dict]:
    """
    Combine vector similarity search with BM25 keyword search.
    Scores are normalized and weighted before merging.
    """
    texts = [doc["text"] for doc in all_documents]
    bm25 = BM25(texts)

    # --- Vector search ---
    collection = get_collection(collection_name)
    query_embedding = get_embedding(query)
    vector_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results * 2,  # retrieve more, then merge
        include=["documents", "metadatas", "distances"]
    )

    # Build vector score map: doc_text -> normalized score (1 - distance for cosine)
    vector_scores: dict[str, float] = {}
    for i in range(len(vector_results["ids"][0])):
        text = vector_results["documents"][0][i]
        score = 1 - vector_results["distances"][0][i]  # convert distance to similarity
        vector_scores[text] = score

    # --- BM25 search ---
    bm25_top = bm25.get_top_n(query, n=n_results * 2)
    max_bm25 = bm25_top[0][1] if bm25_top and bm25_top[0][1] > 0 else 1.0
    bm25_scores: dict[str, float] = {}
    for idx, score in bm25_top:
        normalized = score / max_bm25
        bm25_scores[texts[idx]] = normalized

    # --- Merge scores ---
    all_texts = set(vector_scores.keys()) | set(bm25_scores.keys())
    combined: list[tuple[str, float]] = []
    for text in all_texts:
        v_score = vector_scores.get(text, 0.0) * vector_weight
        b_score = bm25_scores.get(text, 0.0) * bm25_weight
        combined.append((text, v_score + b_score))

    combined.sort(key=lambda x: x[1], reverse=True)
    top_texts = {t for t, _ in combined[:n_results]}

    # Reconstruct result dicts from all_documents
    results = []
    text_to_doc = {doc["text"]: doc for doc in all_documents}
    for text, score in combined[:n_results]:
        doc = text_to_doc.get(text, {})
        results.append({
            "text": text,
            "source": doc.get("source", "Unknown"),
            "category": doc.get("category", "Unknown"),
            "hybrid_score": round(score, 4)
        })

    return results