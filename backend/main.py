from typing import Annotated
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pdf_parser import extract_pages_from_pdf
from pathlib import Path
from chunker import chunk_page
from embedding import create_embedding

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")  # backend/uploads
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"message": "RAG backend is running"}


@app.post("/documents/upload")
async def upload_document(file: Annotated[UploadFile, File()]):
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

    

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "chunks": chunks,
    }
