"""
Creates vector embeddings using a local sentence-transformers model.
No paid API key needed for embeddings.
"""

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

# Load the model once (reused for all calls)
_model = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model so startup stays fast."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of text strings into embedding vectors.

    Args:
        texts: List of text chunks (or a single query as a 1-item list).

    Returns:
        List of embedding vectors (each vector is a list of floats).
    """
    if not texts:
        return []

    model = _get_model()
    vectors = model.encode(texts, show_progress_bar=False)
    # Convert numpy arrays to plain Python lists for ChromaDB
    return [vec.tolist() for vec in vectors]


def embed_query(query: str) -> list[float]:
    """
    Convert a single user query into one embedding vector.

    Args:
        query: The user's question.

    Returns:
        One embedding vector.
    """
    return embed_texts([query])[0]
