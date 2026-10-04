from fastapi import APIRouter

from logging_config import logger

router = APIRouter()


@router.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message": "RAG backend is running"}
