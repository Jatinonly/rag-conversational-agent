from typing import Annotated
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from uuid import uuid4
from redis.exceptions import RedisError
import json

from pdf_parser import extract_pages_from_pdf
from chunker import chunk_page
from rag_retriever import RAGRetriever
from prompt import build_rag_prompt
from llm import generate_answer
from database import SessionLocal, Document, Chunk, Conversation, Message
from vector_store import save_index, load_index
from conversation_rewriter import rewrite_conversation_query
from logging_config import logger
import hashlib
from redis_client import redis_client

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
    conversation_id: str
    question: str
    document_id: str | None = None


def make_cache_key(conversation_id: str, question: str, document_id: str | None) -> str:
    raw = f"{conversation_id}:{question.strip().lower()}:{document_id}"
    return "answer:" + hashlib.sha256(raw.encode()).hexdigest()


def cache_get(key: str):
    try:
        return redis_client.get(key)
    except RedisError:
        logger.warning("Redis unavailable, skipping cache read")
        return None


def cache_set(key: str, value: str, ttl: int = 3600):
    try:
        redis_client.setex(key, ttl, value)
    except RedisError:
        logger.warning("Redis unavailable, skipping cache write")


def clear_answer_cache():
    try:
        for key in redis_client.scan_iter("answer:*"):
            redis_client.delete(key)
    except RedisError:
        logger.warning("Redis unavailable, could not clear cache")


def load_retriever_from_database():
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

            return RAGRetriever(
                chunk_data,
                index=index,
            )

        logger.info("FAISS index not found. Creating new index")

        return RAGRetriever(chunk_data)


retriever = load_retriever_from_database()

logger.info("RAG retriever initialization completed")


@app.get("/")
def root():
    logger.info("Root endpoint called")

    return {"message": "RAG backend is running"}


@app.post("/documents/upload")
async def upload_document(file: Annotated[UploadFile, File()]):
    document_id = str(uuid4())

    logger.info(
        "Document upload started | document_id=%s | filename=%s",
        document_id,
        file.filename,
    )

    global retriever

    file_bytes = await file.read()

    logger.info(
        "File read successfully | document_id=%s | size=%d bytes",
        document_id,
        len(file_bytes),
    )

    file_path = (
        UPLOAD_DIR / f"{document_id}_{file.filename}"
    )  # if user uploads 2 same named file

    file_path.write_bytes(file_bytes)

    logger.info(
        "File saved | document_id=%s | path=%s",
        document_id,
        file_path,
    )

    pages = extract_pages_from_pdf(file_bytes)

    logger.info(
        "PDF extraction completed | document_id=%s | pages=%d",
        document_id,
        len(pages),
    )

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

    logger.info(
        "Document chunking completed | document_id=%s | chunks=%d",
        document_id,
        len(chunks),
    )

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

    logger.info(
        "Document and chunks saved to database | document_id=%s",
        document_id,
    )

    # Add chunks to the in-memory RAG system
    if retriever is None:
        logger.info("Creating new RAG retriever")

        retriever = RAGRetriever(chunks)

    else:
        logger.info("Adding chunks to existing RAG retriever")

        retriever.add_chunks(chunks)

    save_index(retriever.index, "faiss.index")

    logger.info(
        "FAISS index saved | document_id=%s | total_chunks=%d",
        document_id,
        len(retriever.chunks),
    )

    logger.info(
        "Document upload completed | document_id=%s | filename=%s",
        document_id,
        file.filename,
    )

    clear_answer_cache()

    return {
        "filename": file.filename,
        "document_id": document_id,
        "chunks": len(chunks),
        "total_chunks": len(retriever.chunks),
    }


@app.get("/documents")
async def list_documents():
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


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    logger.info(
        "Document deletion started | document_id=%s",
        document_id,
    )

    global retriever

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
    if retriever is not None:
        retriever.remove_document(document_id)

        logger.info(
            "Document removed from in-memory RAG system | document_id=%s",
            document_id,
        )

        if retriever.chunks:
            save_index(retriever.index, "faiss.index")

            logger.info("FAISS index updated after document deletion")

        else:  # means deleted file was the last file and now there are no chunks left.
            retriever = None

            faiss_path = Path("faiss.index")  # remove the faiss.index file.
            if faiss_path.exists():
                faiss_path.unlink()

                logger.info("FAISS index deleted because no chunks remain")

    logger.info(
        "Document deletion completed | document_id=%s",
        document_id,
    )

    clear_answer_cache()

    return {
        "message": "Document deleted",
        "document_id": document_id,
    }


@app.post("/query")
async def query_document(request: QueryRequest):

    logger.info(
        "Query received | conversation_id=%s | document_id=%s | question=%s",
        request.conversation_id,
        request.document_id,
        request.question,
    )

    if retriever is None:
        logger.warning("Query failed because no documents are available")

        return {"error": "No document has been uploaded yet."}

    cache_key = make_cache_key(
        request.conversation_id,
        request.question,
        request.document_id,
    )

    cached = cache_get(cache_key)

    if cached:
        try:
            data = json.loads(cached)
            logger.info("Cache hit")
            return {
                "question": request.question,
                "answer": data["answer"],
                "sources": data["sources"],
                "cached": True,
            }
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("Invalid cache entry, ignoring it")

    logger.info("Cache miss")

    with SessionLocal() as db:
        conversation = db.get(Conversation, request.conversation_id)

        if conversation is None:
            logger.warning(
                "Conversation not found | conversation_id=%s",
                request.conversation_id,
            )
            return {"error": "Conversation not found."}

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == request.conversation_id)
            .order_by(Message.id.desc())
            .limit(6)
            .all()
        )

        messages.reverse()

    logger.info(
        "Conversation history loaded | conversation_id=%s | messages=%d",
        request.conversation_id,
        len(messages),
    )

    history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    if history and any(
        word in request.question.lower().split()
        for word in ["it", "they", "them", "this", "that", "these", "those"]
    ):
        logger.info("Rewriting conversational query")

        search_query = rewrite_conversation_query(
            question=request.question,
            history=history,
        )

        logger.info(
            "Conversation query rewritten | search_query=%s",
            search_query,
        )

    else:
        search_query = request.question

        logger.info("Using original question for retrieval")

    logger.info("Starting document retrieval")

    retrieved_chunks = retriever.search(
        query=search_query,
        top_k=3,
        candidate_k=10,
        rewrite=True,
        multi_query=True,
        document_id=request.document_id,
    )

    logger.info(
        "Document retrieval completed | chunks=%d",
        len(retrieved_chunks),
    )

    prompt = build_rag_prompt(
        question=request.question,
        retrieved_chunks=retrieved_chunks,
        history=history,
    )

    logger.info("RAG prompt built")

    logger.info("Sending prompt to LLM")

    answer = generate_answer(prompt)

    logger.info("LLM response generated")

    # Database Update
    with SessionLocal() as db:
        db.add(
            Message(
                conversation_id=request.conversation_id,
                role="user",
                content=request.question,
            )
        )

        db.add(
            Message(
                conversation_id=request.conversation_id,
                role="assistant",
                content=answer,
            )
        )

        db.commit()

    logger.info(
        "Conversation messages saved | conversation_id=%s",
        request.conversation_id,
    )

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

    cache_set(cache_key, json.dumps({"answer": answer, "sources": sources}))

    logger.info(
        "Query completed | conversation_id=%s | sources=%d",
        request.conversation_id,
        len(sources),
    )

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
        "cached": False,
    }


@app.post("/conversations")
async def create_conversation():
    conversation_id = str(uuid4())

    logger.info(
        "Creating conversation | conversation_id=%s",
        conversation_id,
    )

    with SessionLocal() as db:
        conversation = Conversation(
            id=conversation_id,
        )

        db.add(conversation)
        db.commit()


    logger.info(
        "Conversation created | conversation_id=%s",
        conversation_id,
    )

    return {"conversation_id": conversation_id}


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):

    logger.info(
        "Getting conversation | conversation_id=%s",
        conversation_id,
    )

    with SessionLocal() as db:
        conversation = db.get(Conversation, conversation_id)

        if conversation is None:
            logger.warning(
                "Conversation not found | conversation_id=%s",
                conversation_id,
            )

            return {"error": "Conversation not found."}

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.id)
            .all()
        )

    logger.info(
        "Conversation loaded | conversation_id=%s | messages=%d",
        conversation_id,
        len(messages),
    )

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ],
    }


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):

    logger.info(
        "Deleting conversation | conversation_id=%s",
        conversation_id,
    )

    with SessionLocal() as db:
        conversation = db.get(Conversation, conversation_id)

        if conversation is None:
            logger.warning(
                "Conversation not found | conversation_id=%s",
                conversation_id,
            )

            return {"error": "Conversation not found."}

        db.delete(conversation)
        db.commit()

    logger.info(
        "Conversation deleted | conversation_id=%s",
        conversation_id,
    )

    return {
        "message": "Conversation deleted",
        "conversation_id": conversation_id,
    }
