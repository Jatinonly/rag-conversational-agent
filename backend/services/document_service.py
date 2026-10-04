from pathlib import Path
from uuid import uuid4

from chunker import chunk_document
from database import Chunk, Document, SessionLocal
from logging_config import logger
from pdf_parser import extract_pages_from_pdf
from services import retriever_service
from services.cache_service import clear_answer_cache
from vector_store import save_index

UPLOAD_DIR = Path("uploads")  # backend/uploads
UPLOAD_DIR.mkdir(exist_ok=True)  # if uploads folder not present then create it.


class NoExtractableTextError(ValueError):
    pass


def upload_document(filename: str, file_bytes: bytes) -> dict:
    document_id = str(uuid4())

    logger.info(
        "Document upload started | document_id=%s | filename=%s",
        document_id,
        filename,
    )
    logger.info(
        "File read successfully | document_id=%s | size=%d bytes",
        document_id,
        len(file_bytes),
    )

    pages = extract_pages_from_pdf(file_bytes)
    logger.info(
        "PDF extraction completed | document_id=%s | pages=%d",
        document_id,
        len(pages),
    )

    chunks = chunk_document(
        pages=pages,
        file_name=filename,
        document_id=document_id,
        chunk_size=800,
        overlap=150,
    )
    logger.info(
        "Document chunking completed | document_id=%s | chunks=%d",
        document_id,
        len(chunks),
    )

    if not chunks:
        raise NoExtractableTextError("The PDF contains no extractable text.")
    
    # if user uploads 2 same named file
    file_path = UPLOAD_DIR / f"{document_id}_{filename}"
    file_path.write_bytes(file_bytes)
    
    logger.info(
        "File saved | document_id=%s | path=%s",
        document_id,
        file_path,
    )

    # Save documents + chunks to SQLite
    with SessionLocal() as db:  # Session created, using which SQLAlchemy interact with database.
        document = Document(id=document_id, filename=filename)
        db.add(document)  # only tells that "I want to insert this object"

        for chunk in chunks:
            db.add(
                Chunk(
                    document_id=document_id,
                    text=chunk["text"],
                    page=chunk["page"],
                )
            )

        db.commit()  # actually completes the transaction like add or delete.
        # db.close() # closes this db session -> automatically done when the "with" block ends

    logger.info(
        "Document and chunks saved to database | document_id=%s",
        document_id,
    )

    # Add chunks to the in-memory RAG system
    active_retriever = retriever_service.add_chunks(chunks)
    save_index(active_retriever.index, "faiss.index")

    logger.info(
        "FAISS index saved | document_id=%s | total_chunks=%d",
        document_id,
        len(active_retriever.chunks),
    )
    logger.info(
        "Document upload completed | document_id=%s | filename=%s",
        document_id,
        filename,
    )

    clear_answer_cache()

    return {
        "filename": filename,
        "document_id": document_id,
        "chunks": len(chunks),
        "total_chunks": len(active_retriever.chunks),
    }


def list_documents() -> dict:
    logger.info("Listing documents")

    with SessionLocal() as db:
        # documents = db.query(Document.filename).distinct().all()
        documents = db.query(Document).all()
        logger.info("Found %d documents", len(documents))

        return {
            "documents": [
                {
                    "document_id": document.id,
                    "filename": document.filename,
                }
                for document in documents
            ]
        }


def delete_document(document_id: str) -> dict:
    logger.info(
        "Document deletion started | document_id=%s",
        document_id,
    )

    # From SQLite
    with SessionLocal() as db:
        document = db.get(Document, document_id)

        if document is None:
            logger.warning(
                "Document not found | document_id=%s",
                document_id,
            )
            return {"message": "Document not found"}

        db.delete(document)
        db.commit()

    logger.info(
        "Document deleted from database | document_id=%s",
        document_id,
    )

    # From in-memory RAG system
    retriever_service.remove_document(document_id)
    clear_answer_cache()

    logger.info(
        "Document deletion completed | document_id=%s",
        document_id,
    )

    return {
        "message": "Document deleted",
        "document_id": document_id,
    }
