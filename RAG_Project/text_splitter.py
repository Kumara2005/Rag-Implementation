"""
Splits long text into overlapping chunks, preferring sentence boundaries.
"""

import re

from config import CHUNK_SIZE, CHUNK_OVERLAP


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences (simple, readable approach)."""
    # Keep the punctuation attached to each sentence
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into chunks of roughly `chunk_size` characters.

    Tries to end chunks at sentence boundaries so meaning stays intact.
    Neighboring chunks share `chunk_overlap` characters of context.

    Args:
        text: Full document text.
        chunk_size: Target max characters per chunk.
        chunk_overlap: Characters shared between neighboring chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    # Normalize whitespace a bit (PDF extraction often has odd newlines)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    sentences = _split_into_sentences(text)
    if not sentences:
        return []

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        # If a single sentence is huge, hard-split it
        if len(sentence) > chunk_size:
            if current.strip():
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(sentence):
                pieces = sentence[start : start + chunk_size].strip()
                if pieces:
                    chunks.append(pieces)
                start += chunk_size - chunk_overlap
            continue

        # Would adding this sentence go over the limit?
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence

    if current.strip():
        chunks.append(current.strip())

    # Add overlap by prepending the end of the previous chunk
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-chunk_overlap:]
            overlapped.append(f"{prev_tail} {chunks[i]}".strip())
        chunks = overlapped

    return chunks
