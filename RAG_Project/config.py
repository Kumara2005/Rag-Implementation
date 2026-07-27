"""
Configuration for the RAG demo.
Set your API keys in a .env file (or environment variables) — never commit real keys.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load RAG_Project/.env if present (ignored by git)
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# --------------------------------------------------
# Paths
# --------------------------------------------------
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = BASE_DIR / "vector_db" / "chroma"

# Create folders if they do not exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# API Keys (from environment / .env only — no defaults with secrets)
# --------------------------------------------------
# Google Gemini: https://aistudio.google.com/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# OpenAI (optional alternative): https://platform.openai.com/api-keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Which LLM to use: "gemini" | "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# --------------------------------------------------
# Model settings
# --------------------------------------------------
GEMINI_MODEL = "gemini-3.5-flash"
OPENAI_MODEL = "gpt-4o-mini"

# Local embedding model (free, runs on your machine)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --------------------------------------------------
# Chunking settings
# --------------------------------------------------
CHUNK_SIZE = 1000         # characters per chunk (larger = more context)
CHUNK_OVERLAP = 200       # overlap so answers aren't cut at boundaries

# --------------------------------------------------
# Retrieval settings
# --------------------------------------------------
TOP_K = 6                 # number of similar chunks to retrieve
CHROMA_COLLECTION = "pdf_chunks"
