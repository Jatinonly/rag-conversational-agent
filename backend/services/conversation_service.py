from uuid import uuid4

from database import Conversation, Message, SessionLocal
from logging_config import logger


def create_conversation() -> dict:
    conversation_id = str(uuid4())

    logger.info(
        "Creating conversation | conversation_id=%s",
        conversation_id,
    )

    with SessionLocal() as db:
        db.add(Conversation(id=conversation_id))
        db.commit()

    logger.info(
        "Conversation created | conversation_id=%s",
        conversation_id,
    )

    return {"conversation_id": conversation_id}


def get_conversation(conversation_id: str) -> dict:
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
            {"role": message.role, "content": message.content}
            for message in messages
        ],
    }


def delete_conversation(conversation_id: str) -> dict:
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
