from typing import Annotated
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel

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
    global retriever

    file_bytes = await file.read()

    file_path = UPLOAD_DIR / file.filename

    file_path.write_bytes(file_bytes)

    pages = extract_pages_from_pdf(file_bytes)

    chunks = []

    for page in pages:
        page_chunks = chunk_page(
            page_text=page["text"],
            page_number=page["page"],
            file_name=file.filename,
        )
        chunks.extend(page_chunks)

    retriever = RAGRetriever(chunks)

    return {
        "filename": file.filename,
        "chunks": len(chunks),
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
            "rerank_score": chunk["rerank_score"],
        }
        for chunk in retrieved_chunks
    ]

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }
