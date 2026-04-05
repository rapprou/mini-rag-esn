import os
import psycopg2
import psycopg2.extras
from app.db.supabase import get_supabase


def retrieve_chunks(query_embedding: list[float], top_k: int) -> list[dict]:
    embedding_str = "[" + ",".join(f"{x:.6f}" for x in query_embedding) + "]"

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        conn = None
        try:
            conn = psycopg2.connect(database_url)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                SELECT id, content, document_id,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding_str, embedding_str, top_k),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] psycopg2 failed: {e}")
            if conn:
                conn.close()

    fallback = (
        get_supabase()
        .table("chunks")
        .select("id, document_id, content")
        .limit(top_k)
        .execute()
    )
    for chunk in fallback.data or []:
        chunk["similarity"] = 0.0
    return fallback.data or []


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
