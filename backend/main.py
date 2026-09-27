from typing import Annotated
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel

from pdf_parser import extract_pages_from_pdf
from chunker import chunk_page
from rag_retriever import RAGRetriever

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")  # backend/uploads
UPLOAD_DIR.mkdir(exist_ok=True)  # if uploads folder not present then create it.

retriever = None


class QueryRequest(
    BaseModel
):  # Request should have a field called question, and it should be a string.
    question: str


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

    results = retriever.search(
        query=request.question,
        top_k=3,
    )

    return {
        "question": request.question,
        "results": results,
    }
