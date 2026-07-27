# RAG PDF Demo

A simple **Retrieval-Augmented Generation (RAG)** app: upload a PDF, index it into a local vector database, and ask questions. Answers are grounded in your document using semantic search plus an LLM (Gemini or OpenAI).

---

## Quick start

### 1. Prerequisites

- Python 3.10+ recommended  
- A [Google AI Studio](https://aistudio.google.com/apikey) API key (Gemini), **or** an [OpenAI](https://platform.openai.com/api-keys) API key  

### 2. Install

```bash
cd RAG_Project
pip install -r requirements.txt
```

### 3. Configure API keys

Copy the example env file and add your keys locally (`.env` is gitignored):

```bash
cd RAG_Project
copy .env.example .env
```

Edit `.env`:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-real-key-here
```

For OpenAI, set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...`.

**Do not put real keys in `config.py` or commit `.env`.**

### 4. Run

```bash
cd RAG_Project
streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`).

---

## How to use

1. Upload a **text-based** PDF.  
2. Click **Process PDF** (extract → chunk → embed → store).  
3. Ask a question and click **Get Answer**.  
4. Optionally expand **Retrieved chunks** to see the context sent to the LLM.  

After changing settings or uploading a new file, process the PDF again so the index is rebuilt.

---

## Project structure

```
rag-demo/
├── README.md
├── .gitignore
├── docs/
│   ├── tech.md      # Stack, libraries, features
│   └── flow.md      # Index & query flow
└── RAG_Project/
    ├── app.py              # Streamlit UI
    ├── rag_pipeline.py     # Index + query orchestration
    ├── upload.py           # Save uploaded PDF
    ├── pdf_loader.py       # PDF text extraction
    ├── text_splitter.py    # Chunking
    ├── embedding.py        # Local embeddings
    ├── vector_store.py     # ChromaDB
    ├── llm.py              # Gemini / OpenAI
    ├── config.py           # Settings
    └── requirements.txt
```

---

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/tech.md](docs/tech.md) | Technologies, features, modules, and config |
| [docs/flow.md](docs/flow.md) | Indexing and querying flow |

---

## Stack (summary)

- **UI:** Streamlit  
- **PDF:** pypdf  
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`) — local & free  
- **Vector DB:** ChromaDB (persistent, cosine similarity)  
- **LLM:** Google Gemini (default) or OpenAI  

---

## Notes

- Scanned / image-only PDFs are not supported (no OCR).  
- Re-processing replaces the previous index (one active PDF at a time).  
- First run downloads the embedding model (needs network once).  
- Keep API keys out of git; use env vars and the included `.gitignore`.
