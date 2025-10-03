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

# Check connection
docker-compose exec pgvector psql -U postgres -d postgres -c "SELECT version();"
```