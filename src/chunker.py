def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Split text into overlapping chunks by character count.
    Overlap ensures context isn't lost at chunk boundaries.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


def chunk_documents(documents: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """
    Chunk all documents and return a flat list of chunk dicts.
    Each chunk inherits the parent document's metadata.
    """
    chunked = []
    for doc in documents:
        chunks = chunk_text(doc["text"], chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            chunked.append({
                "id": f"{doc['id']}_chunk{i}",
                "text": chunk,
                "category": doc["category"],
                "source": doc["source"],
                "parent_id": doc["id"]
            })
    return chunked