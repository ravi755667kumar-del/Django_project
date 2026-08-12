"""
rag.py  —  Semantic PDF search using the locally cached HuggingFace model.

- Uses sentence-transformers/all-MiniLM-L6-v2 (cached in /hf_model_cache/).
- Loads the Chroma vector index from /chroma_db/ (built by build_index.py).
- No internet connection required after the first build.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_PATH = BASE_DIR / "chroma_db"
MODEL_CACHE_PATH = BASE_DIR / "hf_model_cache"

# --- Lazy load: only initialized on first chatbot use ---
_retriever = None

def _get_retriever():
    global _retriever
    if _retriever is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma import Chroma

        # Load the model entirely from local disk cache — no internet needed
        embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=str(MODEL_CACHE_PATH),
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        if not VECTOR_DB_PATH.exists():
            raise RuntimeError(
                f"Chroma index not found at {VECTOR_DB_PATH}. "
                "Please run: python shop/build_index.py"
            )

        db = Chroma(
            persist_directory=str(VECTOR_DB_PATH),
            embedding_function=embedding,
        )
        _retriever = db.as_retriever(search_kwargs={"k": 3})

    return _retriever


def search_pdf(question: str) -> str:
    """
    Return the top-3 most relevant chunks from the PDF knowledge base
    for the given question, using semantic (embedding) similarity.
    Falls back to empty string if the index is not yet built.
    """
    try:
        retriever = _get_retriever()
        docs = retriever.invoke(question)
        return "\n\n".join(doc.page_content for doc in docs)
    except Exception as e:
        print(f"[RAG] Warning: Could not retrieve from Chroma — {e}")
        return ""

