from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.document_service import (
    NoExtractableTextError,
    delete_document as delete_document_service,
    list_documents as list_documents_service,
    upload_document as upload_document_service,
)

router = APIRouter(prefix="/documents")


@router.post("/upload")
async def upload_document(file: Annotated[UploadFile, File()]):
    try:
        return upload_document_service(
            file.filename or "uploaded.pdf",
            await file.read(),
        )
    except NoExtractableTextError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("")
async def list_documents():
    return list_documents_service()


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    return delete_document_service(document_id)
