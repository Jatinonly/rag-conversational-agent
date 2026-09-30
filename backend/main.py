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


retriever = None


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

    if retriever is None:
        retriever = RAGRetriever(chunks)

    else:
        retriever.add_chunks(chunks)

    return {
        "filename": file.filename,
        "document_id": document_id,
        "chunks": len(chunks),
        "total_chunks": len(retriever.chunks),
    }


@app.get("/documents")
async def list_documents():
    if retriever is None:
        return {
            "documents": [],
            "error": "No document has been uploaded yet."
        }

    documents = {}

    for chunk in retriever.chunks:
        document_id = chunk["document_id"]

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": chunk["filename"],
                "chunks": 0,
            }

        documents[document_id]["chunks"] += 1

    return {"documents": list(documents.values())}


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    global retriever

    if retriever is None:
        return {"message": "No documents loaded"}

    deleted = retriever.remove_document(document_id)

    if not deleted:
        return {"message": "Document not found"}

    return {
        "message": "Document deleted",
        "total_chunks": len(retriever.chunks),
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
