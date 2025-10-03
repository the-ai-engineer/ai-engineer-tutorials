import psycopg
from pgvector.psycopg import register_vector


DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

def create_connection():
    """Create a database connection and register vector type."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn