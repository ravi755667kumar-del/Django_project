"""
Lightweight RAG replacement.

Instead of FastEmbed + ChromaDB (which require 1GB+ RAM and download ONNX models),
we use a simple TF-IDF-style keyword search over the pre-extracted plain-text
knowledge base. This is fast, uses ~0 extra RAM, and needs no extra packages.
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the pre-extracted plain-text knowledge base
KB_PATH = BASE_DIR / "documents" / "brew_haven_kb.txt"

# Load once at module import — it's just a tiny text file (~2 KB)
_kb_text = ""
_kb_paragraphs = []

def _load_kb():
    global _kb_text, _kb_paragraphs
    if _kb_paragraphs:
        return  # already loaded
    if KB_PATH.exists():
        _kb_text = KB_PATH.read_text(encoding="utf-8")
        # Split into paragraphs (separated by blank lines)
        _kb_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", _kb_text) if p.strip()]
    else:
        _kb_text = ""
        _kb_paragraphs = []


def _score(paragraph: str, query_words: list[str]) -> int:
    """Count how many query words appear in the paragraph (case-insensitive)."""
    para_lower = paragraph.lower()
    return sum(1 for w in query_words if w in para_lower)


def search_pdf(question: str, k: int = 3) -> str:
    """
    Return the top-k most relevant paragraphs from the knowledge base
    for the given question, as a single context string.
    """
    _load_kb()

    if not _kb_paragraphs:
        return ""

    # Tokenise the question into meaningful words (ignore short stop words)
    stop = {"a", "an", "the", "is", "in", "on", "at", "to", "do", "i", "me",
            "my", "we", "you", "it", "of", "for", "and", "or", "be", "can",
            "are", "was", "what", "how", "when", "where", "which", "who"}
    query_words = [w for w in re.findall(r"[a-z]+", question.lower()) if w not in stop and len(w) > 2]

    if not query_words:
        # Fall back: return the first k paragraphs
        return "\n\n".join(_kb_paragraphs[:k])

    # Score every paragraph and pick the top k
    scored = [(para, _score(para, query_words)) for para in _kb_paragraphs]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Take top-k with at least 1 matching word; if none match, return first k
    top = [para for para, score in scored[:k] if score > 0]
    if not top:
        top = [para for para, _ in scored[:k]]

    return "\n\n".join(top)
