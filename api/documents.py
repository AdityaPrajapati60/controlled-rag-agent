from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
import uuid

from api.auth_helpers import get_current_user
from db.database import SessionLocal
from rag.vector_store import get_vector_store
from rag.chunking import extract_and_chunk_pdf  # your existing logic
from models.document import Document
from fastapi import HTTPException

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc_id = str(uuid.uuid4())

    # 🔹 Chunk + embed
    docs = extract_and_chunk_pdf(file)
    for d in docs:
        d.metadata = {
            "doc_id": doc_id,
            "filename": file.filename,
        }

    vector_store = get_vector_store(current_user.id)
    vector_store.add_documents(docs)

    # 🔹 Save document record (SOURCE OF TRUTH)
    db_doc = Document(
        id=doc_id,
        filename=file.filename,
        user_id=current_user.id,
    )
    db.add(db_doc)
    db.commit()

    return {
        "message": "Document ingested successfully",
        "doc_id": doc_id,
        "filename": file.filename,
    }



@router.get("/list")
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from models.document import Document

    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "doc_id": doc.id,
            "filename": doc.filename,
            "uploaded_at": doc.created_at,
        }
        for doc in documents
    ]




@router.delete("/delete/{doc_id}")
def delete_single_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1️⃣ Check source of truth (SQL)
    document = (
        db.query(Document)
        .filter(
            Document.id == doc_id,
            Document.user_id == current_user.id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # 2️⃣ Delete from vector DB
    from rag.vector_store import delete_document
    delete_document(
        user_id=current_user.id,
        doc_id=doc_id
    )

    # 3️⃣ Delete SQL record
    db.delete(document)
    db.commit()

    return {
        "message": f"Document {doc_id} deleted successfully"
    }



@router.delete("/delete-all")
def delete_all_documents(
    current_user=Depends(get_current_user),
):
    from rag.vector_store import delete_all_user_documents

    delete_all_user_documents(
        user_id=current_user.id
    )

    return {
        "message": "All user documents deleted from vector DB"
    }
