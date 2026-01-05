from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from api.auth_helpers import get_current_user
from db.database import SessionLocal
from rag.vector_store import get_vector_store, delete_document
from rag.chunking import extract_and_chunk_pdf
from models.document import Document

router = APIRouter(prefix="/documents", tags=["Documents"])


# ------------------------------------------------
# DB Dependency
# ------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------
# UPLOAD DOCUMENT
# ------------------------------------------------
@router.post("/upload")
def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc_id = str(uuid.uuid4())

    # 1️⃣ Chunk + embed
    docs = extract_and_chunk_pdf(file)

    if not docs:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF contains no extractable text",
        )

    for d in docs:
        d.metadata = {
            "doc_id": doc_id,
            "filename": file.filename,
        }

    vector_store = get_vector_store(current_user.id)
    vector_store.add_documents(docs)
    

    # 2️⃣ Save document metadata (SOURCE OF TRUTH)
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


# ------------------------------------------------
# LIST DOCUMENTS
# ------------------------------------------------
@router.get("/list")
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
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


# ------------------------------------------------
# DELETE SINGLE DOCUMENT
# ------------------------------------------------
@router.delete("/delete/{doc_id}")
def delete_single_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1️⃣ Check SQL source of truth
    document = (
        db.query(Document)
        .filter(
            Document.id == doc_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # 2️⃣ Delete from vector DB
    delete_document(
        user_id=current_user.id,
        doc_id=doc_id,
    )

    # 3️⃣ Delete SQL metadata
    db.delete(document)
    db.commit()

    return {
        "message": f"Document {doc_id} deleted successfully"
    }


# ------------------------------------------------
# DELETE ALL DOCUMENTS (FIXED PATH)
# ------------------------------------------------
@router.delete("/delete-all")
def delete_all_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1️⃣ Delete all vectors
    vector_store = get_vector_store(current_user.id)
    vector_store.delete_collection()

    # 2️⃣ Delete all metadata
    db.query(Document).filter(
        Document.user_id == current_user.id
    ).delete()

    db.commit()

    return {
        "message": "All user documents deleted (vectors + metadata)"
    }
