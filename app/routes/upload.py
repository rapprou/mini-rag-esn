from fastapi import APIRouter, HTTPException, UploadFile, Form
from typing import Annotated

from app.db.supabase import get_supabase
from app.models.schemas import UploadResponse
from app.services.chunker import extract_text, chunk_text
from app.services.embedder import embed_batch

router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_document(
    file: UploadFile,
    title: Annotated[str | None, Form()] = None,
):
    file_bytes = await file.read()
    filename = file.filename or "untitled"
    document_title = title or filename.rsplit(".", 1)[0]

    try:
        text = extract_text(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=422, detail="No text content could be extracted.")

    embeddings = embed_batch(chunks)

    supabase = get_supabase()

    doc_response = (
        supabase.table("documents")
        .insert({"title": document_title, "filename": filename})
        .execute()
    )
    document = doc_response.data[0]
    document_id = document["id"]

    chunk_rows = [
        {
            "document_id": document_id,
            "content": chunk,
            "embedding": embedding,
            "chunk_index": i,
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    supabase.table("chunks").insert(chunk_rows).execute()

    return UploadResponse(
        document_id=document_id,
        title=document_title,
        filename=filename,
        chunk_count=len(chunks),
        message="Document uploaded and indexed successfully.",
    )
