import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ==========================
# Project Base Directory
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================
# PDF Path
# ==========================
PDF_PATH = BASE_DIR / "documents" / "Brew_Haven.pdf"

print("Project Directory :", BASE_DIR)
print("PDF Path          :", PDF_PATH)
print("PDF Exists        :", PDF_PATH.exists())

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
# Split PDF
# ==========================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks.")

# ==========================
# Embedding Model
# ==========================
from langchain_community.embeddings import FastEmbedEmbeddings

embedding = FastEmbedEmbeddings()
# embedding = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     model_kwargs={'local_files_only': True}
# )

# ==========================
# Create Chroma Index
# ==========================
vector_db_path = BASE_DIR / "chroma_db"

db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory=str(vector_db_path)
)

print("\nChroma Index Created Successfully!")
print("Saved at:", vector_db_path)