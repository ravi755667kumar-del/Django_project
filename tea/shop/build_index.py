"""
build_index.py  --  Run this ONCE to build the Chroma vector index from both PDF and TXT knowledge bases.

Steps:
1. Loads Brew_Haven.pdf and brew_haven_kb.txt from the /documents/ folder
2. Splits all text into chunks
3. Embeds using FastEmbed (ONNX-based, no PyTorch needed, ~20MB RAM)
4. Stores the vector index in /chroma_db/

After running this once, the chatbot loads from /chroma_db/ at runtime.
Run with:  python shop/build_index.py
"""

import os
import shutil
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma

# ==========================
# Paths
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "documents" / "Brew_Haven.pdf"
TXT_PATH = BASE_DIR / "documents" / "brew_haven_kb.txt"
VECTOR_DB_PATH = BASE_DIR / "chroma_db"

print("Project Directory :", BASE_DIR)
print("PDF Path          :", PDF_PATH)
print("TXT Path          :", TXT_PATH)

# ==========================
# Wipe old chroma_db
# ==========================
if VECTOR_DB_PATH.exists():
    shutil.rmtree(VECTOR_DB_PATH)
    print("Old chroma_db removed.")

# ==========================
# Load Documents (PDF + TXT)
# ==========================
all_documents = []

if PDF_PATH.exists():
    pdf_loader = PyPDFLoader(str(PDF_PATH))
    pdf_docs = pdf_loader.load()
    all_documents.extend(pdf_docs)
    print(f"Loaded PDF: {len(pdf_docs)} pages.")
else:
    print(f"[Warning] PDF not found: {PDF_PATH}")

if TXT_PATH.exists():
    txt_loader = TextLoader(str(TXT_PATH), encoding="utf-8")
    txt_docs = txt_loader.load()
    all_documents.extend(txt_docs)
    print(f"Loaded TXT knowledge base: {len(txt_docs)} document(s).")
else:
    print(f"[Warning] TXT not found: {TXT_PATH}")

if not all_documents:
    raise FileNotFoundError("No documents found in /documents/ to index!")

# ==========================
# Split all documents into chunks
# ==========================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = splitter.split_documents(all_documents)
print(f"Total chunks created across all documents: {len(chunks)}")

# ==========================
# Load FastEmbed (ONNX-based — no PyTorch, ~20MB RAM)
# ==========================
print("\nLoading FastEmbed model (BAAI/bge-small-en-v1.5 via ONNX)...")

# Save cache inside the project directory so Render doesn't delete it
cache_path = str(PROJECT_DIR / "fastembed_cache")

embedding = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    cache_dir=cache_path
)
print("FastEmbed model ready!")

# ==========================
# Build and Save Chroma Index
# ==========================
print("\nBuilding Chroma vector index from all documents...")
db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory=str(VECTOR_DB_PATH)
)

print("\n[OK] Chroma Index Created Successfully from PDF + TXT!")
print("   Saved at:", VECTOR_DB_PATH)
print("   Total chunks indexed:", len(chunks))
print("\nYou only need to run this script ONCE. The chatbot now searches both sources.")