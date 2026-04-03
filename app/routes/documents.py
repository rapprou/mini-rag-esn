from fastapi import APIRouter, HTTPException

from app.db.supabase import get_supabase
from app.models.schemas import DocumentOut, DeleteResponse

router = APIRouter()


@router.get("", response_model=list[DocumentOut])
def list_documents():
    response = (
        get_supabase()
        .table("documents")
        .select("id, title, filename, created_at, chunk_count")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


@router.delete("/{document_id}", response_model=DeleteResponse)
def delete_document(document_id: int):
    supabase = get_supabase()

    chunks_response = (
        supabase.table("chunks")
        .delete()
        .eq("document_id", document_id)
        .execute()
    )
    deleted_chunks = len(chunks_response.data or [])

    doc_response = (
        supabase.table("documents")
        .delete()
        .eq("id", document_id)
        .execute()
    )
    if not doc_response.data:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found.")

    return DeleteResponse(
        document_id=document_id,
        deleted_chunks=deleted_chunks,
        message="Document and its chunks deleted successfully.",
    )
