from app.db.supabase import get_supabase


def retrieve_chunks(query_embedding: list[float], top_k: int) -> list[dict]:
    response = get_supabase().rpc(
        "match_chunks",
        {"query_embedding": query_embedding, "match_count": top_k},
    ).execute()
    return response.data or []


def enrich_with_document_titles(chunks: list[dict]) -> list[dict]:
    if not chunks:
        return chunks

    document_ids = list({chunk["document_id"] for chunk in chunks})
    response = (
        get_supabase()
        .table("documents")
        .select("id, title")
        .in_("id", document_ids)
        .execute()
    )

    title_by_id = {doc["id"]: doc["title"] for doc in response.data or []}

    for chunk in chunks:
        chunk["document_title"] = title_by_id.get(chunk["document_id"], "Unknown")

    return chunks
