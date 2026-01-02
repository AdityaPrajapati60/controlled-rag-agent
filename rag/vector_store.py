# rag/vector_store.py

import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

PERSIST_DIR = "./chroma_db"
ENV_NAMESPACE = os.getenv("VECTOR_NAMESPACE", "prod")


def get_vector_store(user_id: int) -> Chroma:
    """
    Returns an isolated vector collection per user,
    namespaced per environment.
    """
    return Chroma(
        collection_name=f"{ENV_NAMESPACE}_user_{user_id}_docs",
        embedding_function=embedding_function,
        persist_directory=PERSIST_DIR,
    )


# -------------------------------
#  DELETION UTILITIES
# -------------------------------

def delete_document(user_id: int, doc_id: str) -> None:
    vector_store = get_vector_store(user_id)
    vector_store.delete(where={"doc_id": doc_id})


def delete_all_user_documents(user_id: int) -> None:
    vector_store = get_vector_store(user_id)
    vector_store.delete_collection()
