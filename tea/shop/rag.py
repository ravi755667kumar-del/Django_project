import os
from pathlib import Path


from dotenv import load_dotenv

load_dotenv()
# Authenticate with your token
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent.parent

embedding = FastEmbedEmbeddings()

db = Chroma(
    persist_directory=str(BASE_DIR / "chroma_db"),
    embedding_function=embedding
)


def search_pdf(question):
    results = db.similarity_search(question, k=3)

    context = ""

    for doc in results:
        context += doc.page_content + "\n\n"

    return context