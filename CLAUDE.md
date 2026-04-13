# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mini RAG-ESN is a Retrieval-Augmented Generation (RAG) system built with FastAPI, Supabase (PostgreSQL + pgvector), OpenAI embeddings, and Claude for answer generation. The UI is a French-language Vue.js SPA.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload

# The app serves the frontend at http://localhost:8000/
```

## Environment Setup

Copy `.env.example` to `.env` and fill in:
- `SUPABASE_URL` / `SUPABASE_KEY` — Supabase project credentials
- `ANTHROPIC_API_KEY` — for Claude generation
- `OPENAI_API_KEY` — for embeddings
- `DATABASE_URL` — (optional) direct psycopg2 connection for faster vector search
- `EMBEDDING_MODEL` / `CLAUDE_MODEL` — defaults to `text-embedding-3-small` / `claude-sonnet-4-6`
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — defaults to 500 / 50 tokens

Run `sql/schema.sql` in the Supabase SQL editor once to create tables, the IVFFlat index, and the `match_chunks()` function.

## Architecture

```
POST /upload  →  chunker (PDF/TXT/MD → token chunks)  →  embedder (OpenAI)  →  Supabase (documents + chunks tables)
POST /ask     →  embedder (question)  →  retriever (pgvector cosine search)  →  generator (Claude)  →  AskResponse
GET/DELETE /documents  →  Supabase CRUD
GET /         →  serves frontend/index.html
```

**Layers:**
- `app/routes/` — thin FastAPI handlers, no business logic
- `app/services/` — `chunker`, `embedder`, `retriever`, `generator` are independent modules
- `app/db/supabase.py` — Supabase client singleton
- `app/models/schemas.py` — all Pydantic request/response models

**Vector search strategy:** `retriever.py` tries a direct psycopg2 connection first (using PostgreSQL's `<=>` cosine distance operator), falling back to the Supabase table API if `DATABASE_URL` is not set.

**Chunking:** tiktoken `cl100k_base` tokenizer; chunk boundaries respect token count, not character count.

**Generator system prompt:** instructs Claude to answer only from the provided document chunks and respond in French.
