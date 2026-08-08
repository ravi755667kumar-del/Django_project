import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Lazy globals: not loaded until first use ---
_embedding = None
_db = None


def _get_db():
    """Load FastEmbed + Chroma only on first call, then reuse."""
    global _embedding, _db
    if _db is None:
        from langchain_community.embeddings import FastEmbedEmbeddings
        from langchain_chroma import Chroma
        _embedding = FastEmbedEmbeddings()
        _db = Chroma(
            persist_directory=str(BASE_DIR / "chroma_db"),
            embedding_function=_embedding,
        )
    return _db


def search_pdf(question):
    try:
        db = _get_db()
        results = db.similarity_search(question, k=3)
        context = ""
        for doc in results:
            context += doc.page_content + "\n\n"
        return context
    except Exception as e:
        print(f"[RAG ERROR] {e}")
        return ""
