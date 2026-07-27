# Technologies & Features

This document lists the technologies, libraries, and features used in the RAG PDF Demo project.

---

## Core Concept

**RAG (Retrieval-Augmented Generation)** — answers are grounded in your uploaded PDF. The app retrieves relevant text chunks from a local vector database, then asks an LLM to answer using that context.

---

## Tech Stack

| Layer | Technology | Role |
|-------|------------|------|
| UI | **Streamlit** | Web interface for PDF upload and Q&A |
| PDF parsing | **pypdf** | Extract text from uploaded PDFs |
| Chunking | Custom splitter | Sentence-aware overlapping text chunks |
| Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Local, free text → vector embeddings |
| Vector DB | **ChromaDB** | Persistent local storage + cosine similarity search |
| LLM (default) | **Google Gemini** (`gemini-3.5-flash`) | Generate answers from retrieved context |
| LLM (optional) | **OpenAI** (`gpt-4o-mini`) | Alternative answer generation |
| Language | **Python 3** | Application runtime |
| Config | Environment variables + `config.py` | API keys, models, chunk/retrieval settings |

---

## Dependencies

From `RAG_Project/requirements.txt`:

- `streamlit` — interactive UI
- `pypdf` — PDF text extraction
- `sentence-transformers` — local embedding model
- `chromadb` — vector database
- `google-generativeai` — Gemini API client
- `openai` — OpenAI API client (optional provider)

---

## Features

### 1. PDF upload & indexing
- Upload a text-based PDF via the Streamlit UI
- Save the file under `data/`
- Extract full document text with pypdf
- Split into overlapping chunks (~1000 chars, 200-char overlap)
- Embed chunks locally (no embedding API cost)
- Store chunk text + vectors in ChromaDB (`vector_db/chroma/`)

### 2. Question answering
- Embed the user question with the same local model
- Retrieve top-k similar chunks (default: 6) via cosine similarity
- Build a grounded prompt (context + question)
- Call Gemini or OpenAI to produce the answer
- Show retrieved source chunks in an expandable panel

### 3. Dual LLM provider support
- Switch with `LLM_PROVIDER`: `gemini` (default) or `openai`
- Keys via `GEMINI_API_KEY` / `OPENAI_API_KEY` (env preferred)

### 4. Local-first retrieval
- Embeddings run on your machine (`all-MiniLM-L6-v2`)
- Vector store persists on disk (survives app restarts)
- Re-processing a PDF clears the old collection so indexes do not mix

### 5. Status sidebar
- Live chunk count from the vector DB
- Guidance for API key setup

---

## Project Modules

| File | Responsibility |
|------|----------------|
| `app.py` | Streamlit UI |
| `rag_pipeline.py` | Index + query orchestration |
| `upload.py` | Save uploaded PDF to `data/` |
| `pdf_loader.py` | Extract text with pypdf |
| `text_splitter.py` | Sentence-aware chunking with overlap |
| `embedding.py` | Lazy-loaded sentence-transformers embeddings |
| `vector_store.py` | ChromaDB store / search / clear |
| `llm.py` | Prompt building + Gemini/OpenAI calls |
| `config.py` | Paths, keys, models, chunk/retrieval settings |

---

## Configuration Knobs

| Setting | Default | Purpose |
|---------|---------|---------|
| `CHUNK_SIZE` | 1000 | Target characters per chunk |
| `CHUNK_OVERLAP` | 200 | Shared context between neighboring chunks |
| `TOP_K` | 6 | Number of chunks retrieved per question |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model name |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Gemini model id |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model id |
| `CHROMA_COLLECTION` | `pdf_chunks` | Chroma collection name |

---

## Limitations

- Best with **text-based** PDFs (scanned/image-only PDFs will fail text extraction)
- One active PDF index at a time (re-process replaces previous chunks)
- Requires a valid Gemini or OpenAI API key for answer generation
- Embedding model download on first run (needs network once)
