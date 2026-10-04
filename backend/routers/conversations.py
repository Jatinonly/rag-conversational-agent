from fastapi import APIRouter

from services.conversation_service import (
    create_conversation as create_conversation_service,
    delete_conversation as delete_conversation_service,
    get_conversation as get_conversation_service,
)

router = APIRouter(prefix="/conversations")


@router.post("")
def create_conversation():
    return create_conversation_service()


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    return get_conversation_service(conversation_id)


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    return delete_conversation_service(conversation_id)
