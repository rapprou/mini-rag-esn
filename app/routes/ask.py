from fastapi import APIRouter

from app.models.schemas import AskRequest, AskResponse, ChunkSource
from app.services.embedder import embed_text
from app.services.retriever import retrieve_chunks, enrich_with_document_titles
from app.services.generator import generate_answer

router = APIRouter()


@router.post("", response_model=AskResponse)
def ask(request: AskRequest):
    query_embedding = embed_text(request.question)
    chunks = retrieve_chunks(query_embedding, request.top_k)
    print(f"[DEBUG] retrieve_chunks returned {len(chunks)} chunk(s): {chunks}")
    chunks = enrich_with_document_titles(chunks)

    answer = generate_answer(request.question, chunks)

    sources = [
        ChunkSource(
            document_id=chunk["document_id"],
            document_title=chunk["document_title"],
            content_excerpt=chunk["content"][:200],
            similarity=chunk.get("similarity", 0.0),
        )
        for chunk in chunks
    ]

    return AskResponse(
        question=request.question,
        answer=answer,
        sources=sources,
        chunks_used=len(chunks),
    )
