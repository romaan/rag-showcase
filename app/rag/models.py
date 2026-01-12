from pydantic import BaseModel, Field
from typing import Any

class IngestResult(BaseModel):
    documents: int
    chunks: int

class AskRequest(BaseModel):
    question: str
    top_k: int | None = None
    filter_source: str | None = Field(default=None, description="optional source filter")

class Citation(BaseModel):
    document_id: str
    title: str | None
    source: str
    chunk_id: str
    score: float
    snippet: str

class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    used_top_k: int
