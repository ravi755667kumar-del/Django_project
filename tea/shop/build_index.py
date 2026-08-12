"""
build_index.py  —  Run this ONCE to build the Chroma vector index from the PDF.

Steps:
1. Loads Brew_Haven.pdf from the /documents/ folder
2. Splits into chunks
3. Embeds using the LOCAL HuggingFace model (all-MiniLM-L6-v2) — no API needed
4. Stores the vector index in /chroma_db/

After running this once, the chatbot loads from /chroma_db/ at runtime.
Run with:  python shop/build_index.py
"""

import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ==========================
# Paths
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "documents" / "Brew_Haven.pdf"
VECTOR_DB_PATH = BASE_DIR / "chroma_db"
# The model will be saved here so it never re-downloads
MODEL_CACHE_PATH = BASE_DIR / "hf_model_cache"

print("Project Directory :", BASE_DIR)
print("PDF Path          :", PDF_PATH)
print("PDF Exists        :", PDF_PATH.exists())
print("Model Cache       :", MODEL_CACHE_PATH)

# Stop if PDF is missing
if not PDF_PATH.exists():
    raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

# ==========================
# Load PDF
# ==========================
loader = PyPDFLoader(str(PDF_PATH))
documents = loader.load()
print(f"Loaded {len(documents)} pages.")

# ==========================
# Split PDF into chunks
# ==========================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks.")

# ==========================
# Load HuggingFace Embedding Model Locally
# Downloads once, then loads from disk cache forever
# ==========================
print("\nLoading HuggingFace embedding model (downloads once, cached locally)...")
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=str(MODEL_CACHE_PATH),   # saves model to /hf_model_cache/
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
print("Embedding model ready!")

# ==========================
# Build and Save Chroma Index
# ==========================
print("\nBuilding Chroma vector index...")
db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory=str(VECTOR_DB_PATH)
)

print("\n✅ Chroma Index Created Successfully!")
print("   Saved at:", VECTOR_DB_PATH)
print("   Model cached at:", MODEL_CACHE_PATH)
print("\nYou only need to run this script ONCE. The chatbot now loads from disk.")