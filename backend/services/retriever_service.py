from pathlib import Path

from database import Chunk, SessionLocal
from logging_config import logger
from rag_retriever import RAGRetriever
from vector_store import load_index, save_index


def load_retriever_from_database() -> RAGRetriever | None:
    logger.info("Loading retriever from database")

    with SessionLocal() as db:
        chunks = db.query(Chunk).order_by(Chunk.id).all()

        if not chunks:
            logger.info("No chunks found in database")
            return None

        logger.info("Loaded %d chunks from database", len(chunks))

        chunk_data = [
            {
                "text": chunk.text,
                "page": chunk.page,
                "document_id": chunk.document_id,
                "filename": chunk.document.filename,
            }
            for chunk in chunks
        ]

        faiss_path = Path("faiss.index")

        if faiss_path.exists():
            logger.info("Existing FAISS index found. Loading index")
            index = load_index(str(faiss_path))
            logger.info("FAISS index loaded successfully")
            return RAGRetriever(chunk_data, index=index)

        logger.info("FAISS index not found. Creating new index")
        return RAGRetriever(chunk_data)


retriever = load_retriever_from_database()
logger.info("RAG retriever initialization completed")


def get_retriever() -> RAGRetriever | None:
    return retriever


def add_chunks(chunks: list[dict]) -> RAGRetriever:
    global retriever

    if retriever is None:
        logger.info("Creating new RAG retriever")
        retriever = RAGRetriever(chunks)
    else:
        logger.info("Adding chunks to existing RAG retriever")
        retriever.add_chunks(chunks)

    return retriever


def remove_document(document_id: str) -> None:
    global retriever

    if retriever is None:
        return

    retriever.remove_document(document_id)
    logger.info(
        "Document removed from in-memory RAG system | document_id=%s",
        document_id,
    )

    if retriever.chunks:
        save_index(retriever.index, "faiss.index")
        logger.info("FAISS index updated after document deletion")
        return

    retriever = None
    faiss_path = Path("faiss.index")  # remove the faiss.index file.
    if faiss_path.exists():
        faiss_path.unlink()
        logger.info("FAISS index deleted because no chunks remain")
