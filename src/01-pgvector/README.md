# PostgreSQL + PGVector for AI Applications

A practical guide to using PostgreSQL with pgvector for building RAG (Retrieval Augmented Generation) applications.

## What You'll Learn

- Setting up PostgreSQL with pgvector extension
- Storing and searching vector embeddings
- Building a simple RAG system

## Prerequisites
- Docker and Docker Compose
- Python
- OpenAI API key
---

## 1. Database Setup

### Install PostgreSQL Client Tools

```bash
# macOS
brew install libpq
```

### Create Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
services:
  pgvector:
    image: pgvector/pgvector:pg17
    container_name: pgvector
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    volumes:
      - pgvector_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  pgvector_data:
    driver: local
```

### Start the Database

```bash
# Start PostgreSQL with pgvector
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f pgvector
```

### Connect to Database

```bash
# Option 1: Using psql client
psql postgresql://postgres:postgres@localhost:5432/postgres

# Option 2: Via Docker (if psql not installed)
docker-compose exec pgvector psql -U postgres -d postgres
```

---

## 2. Create the Schema

### Understanding the Architecture

For RAG applications, we use a **document/chunk** architecture:

- **Documents**: Original source files (PDFs, markdown, etc.)
- **Chunks**: Smaller pieces of documents that are embedded and searchable

This separation allows you to:
- Track source documents
- Search efficiently with smaller chunks
- Reconstruct context when needed

### Create Tables

Create `schema.sql`:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Clean slate (for development)
DROP TABLE IF EXISTS faq_chunks CASCADE;
DROP TABLE IF EXISTS faq_documents CASCADE;

-- Source documents
CREATE TABLE faq_documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Embedded chunks for search