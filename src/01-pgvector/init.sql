-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Clean slate (for development)
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- Source documents
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Embedded chunks for search
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI embedding size
    chunk_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vector similarity search index (HNSW is fastest)
CREATE INDEX idx_chunks_embedding 
ON chunks 
USING hnsw (embedding vector_cosine_ops);

-- Quick document lookup
CREATE INDEX idx_chunks_document_id 
ON chunks(document_id);