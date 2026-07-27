"""
Stores and retrieves vectors using ChromaDB (local, file-based).
"""

import chromadb
from chromadb.config import Settings

from config import VECTOR_DB_DIR, CHROMA_COLLECTION, TOP_K


def _get_client() -> chromadb.PersistentClient:
    """Create a ChromaDB client that saves data under vector_db/chroma/."""
    return chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def _get_collection():
    """Get or create the PDF chunks collection."""
    client = _get_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},  # cosine similarity
    )


def clear_collection() -> None:
    """Delete all stored chunks (used before re-indexing a new PDF)."""
    client = _get_client()
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass  # collection may not exist yet
    # Recreate empty collection
    _get_collection()


def store_chunks(chunks: list[str], embeddings: list[list[float]]) -> int:
    """
    Save text chunks + their embeddings into ChromaDB.

    Args:
        chunks: List of text chunks.
        embeddings: Matching list of embedding vectors.

    Returns:
        Number of chunks stored.
    """
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")

    # Start fresh so old PDF data does not mix with the new one
    clear_collection()
    collection = _get_collection()

    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
    )

    return len(chunks)


def search_similar(query_embedding: list[float], top_k: int = TOP_K) -> list[str]:
    """
    Find the most similar chunks to a query embedding.

    Args:
        query_embedding: Embedding vector of the user question.
        top_k: How many chunks to return.

    Returns:
        List of the most relevant text chunks.
    """
    collection = _get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    # results["documents"] is a list of lists (one per query)
    documents = results.get("documents", [[]])[0]
    return documents


def get_chunk_count() -> int:
    """Return how many chunks are currently stored."""
    try:
        return _get_collection().count()
    except Exception:
        return 0
