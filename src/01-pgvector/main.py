import psycopg

from openai import OpenAI

from pgvector.psycopg import register_vector


## Database connection and setup
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"


def create_connection():
    """Create a database connection and register vector type."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


## Embedding generation using OpenAI

client = OpenAI(api_key="your-api-key")


def get_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small", input=text, dimensions=1536
    )
    return response.data[0].embedding
