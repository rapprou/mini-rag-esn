from datetime import datetime
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


class ChunkSource(BaseModel):
    document_id: int
    document_title: str
    content_excerpt: str
    similarity: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[ChunkSource]
    chunks_used: int


class DocumentOut(BaseModel):
    id: int
    title: str
    filename: str
    created_at: datetime
    chunk_count: int


class UploadResponse(BaseModel):
    document_id: int
    title: str
    filename: str
    chunk_count: int
    message: str


class DeleteResponse(BaseModel):
    document_id: int
    deleted_chunks: int
    message: str
