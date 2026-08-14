"""
rag.py  --  Semantic PDF search using FastEmbed (ONNX-based, no PyTorch).

- Uses BAAI/bge-small-en-v1.5 via FastEmbed (~20MB RAM, no API token needed).
- Loads the Chroma vector index from /chroma_db/ (built by build_index.py).
- No internet connection required after the first build.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_PATH = BASE_DIR / "chroma_db"

# --- Lazy load: only initialized on first chatbot use ---
_retriever = None

def _get_retriever():
    global _retriever
    if _retriever is None:
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
        from langchain_chroma import Chroma

        if not VECTOR_DB_PATH.exists():
            raise RuntimeError(
                f"Chroma index not found at {VECTOR_DB_PATH}. "
                "Please run: python shop/build_index.py"
            )

        # Save cache inside the project directory so Render doesn't delete it
        cache_path = str(VECTOR_DB_PATH.parent.parent / "fastembed_cache")
        
        # FastEmbed: ONNX-based, no PyTorch, ~20MB RAM, no API token needed
        embedding = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            cache_dir=cache_path
        )

        db = Chroma(
            persist_directory=str(VECTOR_DB_PATH),
            embedding_function=embedding,
        )
        _retriever = db.as_retriever(search_kwargs={"k": 3})

    return _retriever


def search_pdf(query: str) -> str:
    """Search the Chroma vector DB and return the top matching text chunks."""
    try:
        retriever = _get_retriever()
        docs = retriever.invoke(query)
        if not docs:
            return ""
        return "\n\n".join(doc.page_content for doc in docs)
    except Exception as e:
        print(f"[RAG] Warning: Could not retrieve from Chroma — {e}")
        return ""
