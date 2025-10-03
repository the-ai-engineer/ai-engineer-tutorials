import psycopg
from pgvector.psycopg import register_vector

DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"


def create_connection():
    """Create a database connection and register vector type."""
    try:
        conn = psycopg.connect(DATABASE_URL)
        register_vector(conn)
        print("✅ Connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise


c = create_connection()
