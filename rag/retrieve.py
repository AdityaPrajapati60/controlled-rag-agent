#rag/retrieve.py
from rag.vector_store import get_vector_store


def retrieve_context(query: str, user_id: int, k: int = 4) -> str:
    vector_store = get_vector_store(user_id)
    results = vector_store.similarity_search(query, k=k)

    if not results:
        return ""

    return "\n\n".join(doc.page_content for doc in results)
