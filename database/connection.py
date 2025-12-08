from contextlib import contextmanager
import sqlite3
from app.core.config import DB_PATH

@contextmanager
def get_db_connection():
    """Context manager for safe database connections."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for this connection
        conn.execute("PRAGMA journal_mode=WAL;") 
        yield conn
    except Exception as e:
        # Log error or handle it
        print(f"Database error: {e}")
        raise e
    finally:
        if conn:
            conn.close()
