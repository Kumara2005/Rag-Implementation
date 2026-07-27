"""
Complete RAG workflow:

  Index path:  PDF -> text -> chunks -> embeddings -> vector DB
  Query path:  question -> embedding -> similar chunks -> LLM -> answer
"""

from pathlib import Path

from upload import save_uploaded_pdf
from pdf_loader import extract_text_from_pdf
from text_splitter import split_text
from embedding import embed_texts, embed_query
from vector_store import store_chunks, search_similar, get_chunk_count
from llm import generate_answer


def process_pdf(uploaded_file) -> dict:
    """
    Full indexing pipeline for an uploaded PDF.

    Steps:
      1. Save the PDF to data/
      2. Extract text
      3. Split into chunks
      4. Create embeddings
      5. Store in ChromaDB

    Returns:
        A small status dict (path, chunk count, etc.).
    """
    # 1. Save PDF
    pdf_path = save_uploaded_pdf(uploaded_file)

    # 2. Extract text
    text = extract_text_from_pdf(pdf_path)

    # 3. Split into chunks
    chunks = split_text(text)
    if not chunks:
        raise ValueError("No chunks created — PDF may be empty.")

    # 4. Create embeddings for every chunk
    embeddings = embed_texts(chunks)

    # 5. Store in vector DB
    stored = store_chunks(chunks, embeddings)

    return {
        "pdf_path": str(pdf_path),
        "text_length": len(text),
        "num_chunks": stored,
    }


def process_pdf_from_path(pdf_path: str | Path) -> dict:
    """
    Same as process_pdf, but takes a file path instead of an upload object.
    Useful for testing without Streamlit.
    """
    pdf_path = Path(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text(text)
    if not chunks:
        raise ValueError("No chunks created — PDF may be empty.")

    embeddings = embed_texts(chunks)
    stored = store_chunks(chunks, embeddings)

    return {
        "pdf_path": str(pdf_path),
        "text_length": len(text),
        "num_chunks": stored,
    }


def ask_question(question: str) -> dict:
    """
    Full query pipeline.

    Steps:
      1. Embed the user question
      2. Find similar chunks in the vector DB
      3. Send chunks + question to the LLM
      4. Return the answer (and the retrieved chunks)

    Returns:
        Dict with 'answer' and 'sources' (retrieved chunks).
    """
    question = (question or "").strip()
    if not question:
        return {"answer": "Please enter a question.", "sources": []}

    if get_chunk_count() == 0:
        return {
            "answer": "No PDF has been processed yet. Please upload a PDF first.",
            "sources": [],
        }

    # 1. Embed the question
    query_vector = embed_query(question)

    # 2. Retrieve similar chunks
    similar_chunks = search_similar(query_vector)

    # 3. Ask the LLM
    answer = generate_answer(question, similar_chunks)

    return {
        "answer": answer,
        "sources": similar_chunks,
    }
