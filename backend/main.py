from typing import Annotated
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
import uuid

from pdf_parser import extract_pages_from_pdf
from chunker import chunk_page
from rag_retriever import RAGRetriever
from prompt import build_rag_prompt
from llm import generate_answer
from database import SessionLocal, Document, Chunk
from vector_store import save_index, load_index

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")  # backend/uploads
UPLOAD_DIR.mkdir(exist_ok=True)  # if uploads folder not present then create it.


class QueryRequest(
    BaseModel
):  # Request should have a field called question, and it should be a string.
    question: str


def load_retriever_from_database():
    with SessionLocal() as db:
        chunks = db.query(Chunk).order_by(Chunk.id).all()

        if not chunks:
            return None

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
            index = load_index(str(faiss_path))

            return RAGRetriever(
                chunk_data,
                index=index,
            )

        return RAGRetriever(chunk_data)


retriever = load_retriever_from_database()


@app.get("/")
def root():
    return {"message": "RAG backend is running"}


@app.post("/documents/upload")
async def upload_document(file: Annotated[UploadFile, File()]):
    document_id = str(uuid.uuid4())

    global retriever

    file_bytes = await file.read()

    file_path = (
        UPLOAD_DIR / f"{document_id}_{file.filename}"
    )  # if user uploads 2 same named file

    file_path.write_bytes(file_bytes)

    pages = extract_pages_from_pdf(file_bytes)

    chunks = []

    for page in pages:
        page_chunks = chunk_page(
            page_text=page["text"],
            page_number=page["page"],
            file_name=file.filename,
            document_id=document_id,
            chunk_size=1000,
            overlap=200,
        )
        chunks.extend(page_chunks)

    # Save documents + chunks to SQLite
    with SessionLocal() as db:  # Session created, using which SQLAlchemy interact with database.
        document = Document(
            id=document_id,
            filename=file.filename,
        )

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

    # Add chunks to the in-memory RAG system
    if retriever is None:
        retriever = RAGRetriever(chunks)

    else:
        retriever.add_chunks(chunks)

    save_index(retriever.index, "faiss.index")

    return {
        "filename": file.filename,
        "document_id": document_id,
        "chunks": len(chunks),
        "total_chunks": len(retriever.chunks),
    }


@app.get("/documents")
async def list_documents():
    with SessionLocal() as db:
        # documents = db.query(Document.filename).distinct().all()
        documents = db.query(Document).all()

        return {
            "documents": [
                {
                    "document_id": document.id,
                    "filename": document.filename,
                }
                for document in documents
            ]
        }


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    global retriever

    # From SQLite
    with SessionLocal() as db:
        document = db.get(Document, document_id)

        if document is None:
            return {"message": "Document not found"}

        db.delete(document)
        db.commit()

    # From in-memory RAG system
    if retriever is not None:
        retriever.remove_document(document_id)

        if retriever.chunks:
            save_index(retriever.index, "faiss.index")
        else:  # means deleted file was the last file and now there are no chunks left.
            retriever = None

            faiss_path = Path("faiss.index")  # remove the faiss.index file.
            if faiss_path.exists():
                faiss_path.unlink()

    return {
        "message": "Document deleted",
        "document_id": document_id,
    }


@app.post("/query")
async def query_document(request: QueryRequest):
    if retriever is None:
        return {"error": "No document has been uploaded yet."}

    retrieved_chunks = retriever.search(
        query=request.question,
        top_k=3,
        candidate_k=10,
        rewrite=True,
        multi_query=True,
    )

    prompt = build_rag_prompt(
        question=request.question,
        retrieved_chunks=retrieved_chunks,
    )

    answer = generate_answer(prompt)

    sources = [
        {
            "page": chunk["page"],
            "text": chunk["text"],
            "filename": chunk["filename"],
            "document_id": chunk["document_id"],
            "rerank_score": chunk["rerank_score"],
        }
        for chunk in retrieved_chunks
    ]

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }
