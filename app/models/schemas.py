from datetime import datetime
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


class ChunkSource(BaseModel):
    document_id: str
    document_title: str
    content_excerpt: str
    similarity: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[ChunkSource]
    chunks_used: int


class DocumentOut(BaseModel):
    id: str
    title: str
    filename: str
    created_at: datetime
    chunk_count: int = 0


class UploadResponse(BaseModel):
    document_id: str
    title: str
    filename: str
    chunk_count: int
    message: str


class DeleteResponse(BaseModel):
    document_id: str
    deleted_chunks: int
    message: str
