import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from routers.documents import upload_document
from services import document_service


def test_upload_rejects_pdf_without_extractable_text(tmp_path, monkeypatch):
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(
        document_service,
        "extract_pages_from_pdf",
        lambda _: [{"page": 1, "text": ""}],
    )

    upload = UploadFile(filename="empty.pdf", file=BytesIO(b"%PDF-empty"))

    with pytest.raises(HTTPException) as error:
        asyncio.run(upload_document(upload))

    assert error.value.status_code == 422
    assert error.value.detail == "The PDF contains no extractable text."
    assert list(tmp_path.iterdir()) == []
