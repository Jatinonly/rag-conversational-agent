import json

from conversation_rewriter import rewrite_conversation_query
from database import Conversation, Message, SessionLocal
from llm import generate_answer
from logging_config import logger
from prompt import build_rag_prompt
from schemas import QueryRequest
from services import retriever_service
from services.cache_service import cache_get, cache_set, make_cache_key


def query_document(request: QueryRequest) -> dict:
    logger.info(
        "Query received | conversation_id=%s | document_id=%s | question=%s",
        request.conversation_id,
        request.document_id,
        request.question,
    )

    active_retriever = retriever_service.get_retriever()
    if active_retriever is None:
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
        {"role": message.role, "content": message.content}
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
    retrieved_chunks = active_retriever.search(
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
