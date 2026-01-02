from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import PyPDF2
import io


def extract_and_chunk_pdf(file) -> List[Document]:
    """
    Extract text from PDF and split into clean chunks.
    """

    # 1️⃣ Read PDF bytes
    pdf_bytes = file.file.read()
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    if not full_text.strip():
        return []

    # 2️⃣ Chunking (THIS is critical)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    chunks = splitter.split_text(full_text)

    # 3️⃣ Convert to Documents
    documents = [
        Document(page_content=chunk)
        for chunk in chunks
    ]

    return documents
