-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT NOT NULL,
    filename    TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    chunk_count INT NOT NULL DEFAULT 0
);

-- Chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content      TEXT NOT NULL,
    embedding    VECTOR(1536),
    chunk_index  INT NOT NULL
);

-- Index for fast similarity search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING ivfflat (embedding vector_cosine_ops);

-- match_chunks function
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding VECTOR(1536),
    match_count     INT
)
RETURNS TABLE (
    id           UUID,
    document_id  UUID,
    content      TEXT,
    chunk_index  INT,
    similarity   FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        c.id,
        c.document_id,
        c.content,
        c.chunk_index,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM chunks c
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
$$;
