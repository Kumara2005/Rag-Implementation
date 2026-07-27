# How It Works — Application Flow

This document explains the end-to-end flow of the RAG PDF Demo: indexing a PDF and answering questions from it.

---

## High-Level Overview

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Upload PDF │ ──► │  Index Pipeline  │ ──► │  ChromaDB   │
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                    │
┌─────────────┐     ┌──────────────────┐            │
│ Ask Question│ ──► │  Query Pipeline  │ ◄──────────┘
└─────────────┘     └────────┬─────────┘
                             │
                             ▼
                      ┌─────────────┐
                      │ Gemini /    │
                      │ OpenAI LLM  │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │   Answer    │
                      └─────────────┘
```

There are two main paths:

1. **Index path** — turn a PDF into searchable vectors  
2. **Query path** — retrieve relevant chunks and generate an answer  

Both are wired together in `rag_pipeline.py` and exposed in the Streamlit UI (`app.py`).

---

## User Journey (UI)

1. Open the Streamlit app.
2. Upload a PDF and click **Process PDF**.
3. Wait while text is extracted, chunked, embedded, and stored.
4. Sidebar shows how many chunks are in the vector DB.
5. Type a question and click **Get Answer**.
6. Read the answer; optionally expand **Retrieved chunks** to see the context sent to the LLM.

---

## Index Path (Process PDF)

Entry point: `process_pdf()` in `rag_pipeline.py` (or `process_pdf_from_path()` for local testing).

```
PDF upload
    │
    ▼
1. save_uploaded_pdf()          → data/uploaded_pdf.pdf
    │
    ▼
2. extract_text_from_pdf()      → full document text (pypdf)
    │
    ▼
3. split_text()                 → overlapping text chunks
    │
    ▼
4. embed_texts()                → vectors (sentence-transformers)
    │
    ▼
5. store_chunks()               → ChromaDB (clears old index first)
```

### Step details

| Step | Module | What happens |
|------|--------|--------------|
| 1. Save | `upload.py` | Writes the Streamlit upload to `data/uploaded_pdf.pdf` |
| 2. Extract | `pdf_loader.py` | Reads every page; joins non-empty page text. Fails if no text (e.g. scanned PDF) |
| 3. Chunk | `text_splitter.py` | Splits on sentence boundaries; target size 1000 chars with 200-char overlap |
| 4. Embed | `embedding.py` | Encodes each chunk with `all-MiniLM-L6-v2` (model loaded once, lazily) |
| 5. Store | `vector_store.py` | Deletes previous collection, then adds new documents + embeddings under `pdf_chunks` |

**Why clear before store?**  
This demo keeps one active PDF index. Clearing avoids mixing chunks from an old document with a new one.

**Return value:** path, character count, and number of chunks stored (shown as a success message in the UI).

---

## Query Path (Ask a Question)

Entry point: `ask_question()` in `rag_pipeline.py`.

```
User question
    │
    ▼
0. Validation
   - empty question? → prompt user
   - zero chunks?    → ask to upload/process PDF first
    │
    ▼
1. embed_query()                → one query vector
    │
    ▼
2. search_similar()             → top-k closest chunks (cosine)
    │
    ▼
3. generate_answer()            → LLM answer from context + question
    │
    ▼
Return { answer, sources }
```

### Step details

| Step | Module | What happens |
|------|--------|--------------|
| 0. Guard | `rag_pipeline.py` | Ensures a question exists and the vector DB is not empty |
| 1. Embed | `embedding.py` | Same model as indexing so query and docs share one vector space |
| 2. Retrieve | `vector_store.py` | ChromaDB cosine search; returns up to `TOP_K` (default 6) documents |
| 3. Generate | `llm.py` | Builds a grounded prompt; calls Gemini or OpenAI based on `LLM_PROVIDER` |

### Prompt behavior

The LLM is instructed to:

- Answer from the retrieved CONTEXT when possible  
- Use partial context when coverage is incomplete  
- Avoid inventing facts not supported by the context  
- Refuse only when context is truly unrelated  

The UI shows the answer and, in an expander, the source chunks that were sent as context.

---

## Data Flow Diagram

```
                    ┌──────────────────────────────────────────┐
                    │              INDEXING                     │
                    │                                          │
  PDF ──► Text ──► Chunks ──► Embeddings ──► ChromaDB         │
                    │              (persist on disk)           │
                    └──────────────────────────────────────────┘
                                         │
                                         │ similarity search
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │              QUERYING                     │
                    │                                          │
  Question ──► Embedding ──► Top-K Chunks ──► Prompt ──► LLM  │
                                                    │          │
                                                    ▼          │
                                                 Answer        │
                    └──────────────────────────────────────────┘
```

---

## Storage Layout

| Path | Contents |
|------|----------|
| `RAG_Project/data/` | Saved uploaded PDF (`uploaded_pdf.pdf`) |
| `RAG_Project/vector_db/chroma/` | Persistent ChromaDB files |
| Collection `pdf_chunks` | Chunk IDs (`chunk_0`, `chunk_1`, …), documents, embeddings |

---

## Error / Edge Cases

| Situation | Behavior |
|-----------|----------|
| Empty or image-only PDF | Text extraction raises; UI shows processing error |
| No chunks created | Indexing raises `ValueError` |
| Question before indexing | Returns a friendly message to upload a PDF first |
| Missing API key | LLM call raises with setup instructions |
| Unknown `LLM_PROVIDER` | Raises with allowed values (`gemini` / `openai`) |

---

## Sequence Summary

**Indexing:** Upload → Save → Extract → Chunk → Embed → Store  

**Querying:** Question → Embed → Retrieve → Prompt LLM → Answer (+ sources)
