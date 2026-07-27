"""
Simple Streamlit UI for the RAG demo.

Flow:
  1. Upload a PDF
  2. Process it (chunk + embed + store)
  3. Ask a question
  4. Get an answer grounded in the PDF
"""

import streamlit as st

from rag_pipeline import process_pdf, ask_question
from vector_store import get_chunk_count


# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(
    page_title="RAG PDF Demo",
    page_icon="📄",
    layout="centered",
)

st.title("RAG PDF Demo")
st.write(
    "Upload a PDF → process into chunks & embeddings → ask questions. "
    "Answers come from your document via a vector search + LLM."
)
st.info(
    "After changing settings or uploading a new file, click **Process PDF** again "
    "so chunks are rebuilt with the latest settings."
)

# --------------------------------------------------
# Sidebar: status
# --------------------------------------------------
with st.sidebar:
    st.header("Status")
    chunk_count = get_chunk_count()
    if chunk_count > 0:
        st.success(f"{chunk_count} chunks in vector DB")
    else:
        st.info("No PDF indexed yet")

    st.markdown("---")
    st.caption(
        "Set `GEMINI_API_KEY` (or `OPENAI_API_KEY`) "
        "in your environment or in `config.py`."
    )

# --------------------------------------------------
# Step 1: Upload & process PDF
# --------------------------------------------------
st.header("1. Upload PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a text-based PDF (not a scanned image PDF).",
)

if uploaded_file is not None:
    if st.button("Process PDF", type="primary"):
        with st.spinner("Extracting text → chunking → embedding → storing..."):
            try:
                result = process_pdf(uploaded_file)
                st.success(
                    f"Done! Extracted {result['text_length']} characters "
                    f"into {result['num_chunks']} chunks."
                )
                st.rerun()
            except Exception as e:
                st.error(f"Processing failed: {e}")

# --------------------------------------------------
# Step 2: Ask a question
# --------------------------------------------------
st.header("2. Ask a question")

question = st.text_input(
    "Your question",
    placeholder="e.g. What is the main topic of this document?",
)

if st.button("Get Answer", type="primary", disabled=not question.strip()):
    with st.spinner("Embedding query → searching vector DB → asking LLM..."):
        try:
            result = ask_question(question)
            st.subheader("Answer")
            st.write(result["answer"])

            if result["sources"]:
                with st.expander("Retrieved chunks (context sent to LLM)"):
                    for i, chunk in enumerate(result["sources"], start=1):
                        st.markdown(f"**Chunk {i}**")
                        st.text(chunk)
                        st.markdown("---")
        except Exception as e:
            st.error(f"Query failed: {e}")
