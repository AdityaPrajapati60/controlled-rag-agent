#rag/retrieve.py
from rag.vector_store import get_vector_store


def retrieve_context(query: str, user_id: int, k: int = 4) -> str | None:
    vector_store = get_vector_store(user_id)

    # 🔒 Check if user has ANY documents at all
    if vector_store._collection.count() == 0:
        return None  # ← NO DOCUMENT EXISTS

    results = vector_store.similarity_search(query, k=k)

    if not results:
        return ""  # ← DOC EXISTS, BUT ANSWER NOT FOUND

    return "\n\n".join(doc.page_content for doc in results)
