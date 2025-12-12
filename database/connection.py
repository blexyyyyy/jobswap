from contextlib import contextmanager
import os
import sqlite3

# Check if we're in production (PostgreSQL) or development (SQLite)
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor

@contextmanager
def get_db_connection():
    """Context manager for safe database connections.
    Supports both SQLite (development) and PostgreSQL (production).
    """
    conn = None
    try:
        if USE_POSTGRES:
            # PostgreSQL connection for production
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            yield conn
        else:
            # SQLite connection for development
            from app.core.config import DB_PATH
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            yield conn
    except Exception as e:
        print(f"Database error: {e}")
        if conn and USE_POSTGRES:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
