from fastapi import APIRouter

from schemas import QueryRequest
from services.query_service import query_document as process_query

router = APIRouter()


@router.post("/query")
async def query_document(request: QueryRequest):
    return process_query(request)
