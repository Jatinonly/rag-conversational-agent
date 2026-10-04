from pydantic import BaseModel


class QueryRequest(BaseModel):  # Request should have a field called question, and it should be a string.
    conversation_id: str
    question: str
    document_id: str | None = None
