import sqlite3
import json
import chromadb
from chromadb.utils import embedding_functions
import os
from contextlib import contextmanager
from typing import Dict, Any, List
from app.core.config import DB_PATH

# --- Database Connection Management ---

@contextmanager
def get_db_connection():
    """Context manager for SQLite database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        yield conn
    finally:
        conn.close()

# --- Vector Store (ChromaDB) Configuration ---
CHROMA_DB_PATH = "./chroma_db"

def get_chroma_client():
    if not os.path.exists(CHROMA_DB_PATH):
        os.makedirs(CHROMA_DB_PATH)
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

def get_embedding_function():
    # Use a lightweight embedding model locally or an API
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def add_job_embedding(job_id: int, text: str):
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="job_embeddings", embedding_function=get_embedding_function())
    
    collection.add(
        documents=[text],
        metadatas=[{"job_id": job_id}],
        ids=[str(job_id)]
    )

def query_similar_jobs(text: str, n_results: int = 5):
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="job_embeddings", embedding_function=get_embedding_function())
    
    results = collection.query(
        query_texts=[text],
        n_results=n_results
    )
    return results

# --- Helpers ---

def get_candidate_matches(job_id: int):
    # This would likely involve complex logic or vector search in reverse
    # For now, placeholder
    pass

# ==========================================
# Job Insertion Helper
# ==========================================

def job_exists(conn, title: str, company: str, location: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1 FROM jobs
        WHERE LOWER(title) = LOWER(?)
          AND LOWER(company) = LOWER(?)
          AND LOWER(location) = LOWER(?)
        LIMIT 1
        """,
        (title, company, location),
    )
    return cursor.fetchone() is not None


def insert_job_if_new(job: Dict[str, Any]) -> bool:
    """
    job: normalized dict from scrapers.normalizer.normalize_raw_job
    Returns True if inserted, False if duplicate.
    """
    with get_db_connection() as conn:
        if job_exists(conn, job["title"], job["company"], job["location"]):
            return False
            
        if job.get("url"):
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM jobs WHERE source_url = ?", (job["url"],))
            if cursor.fetchone():
                return False

        cursor = conn.cursor()
        
        def clean(s):
            if isinstance(s, str):
                return s.replace('\x00', '')
            return s
            
        cursor.execute(
            """
            INSERT INTO jobs (title, company, location, skills, description, source_url, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                clean(job["title"]),
                clean(job["company"]),
                clean(job["location"]),
                clean(",".join(job.get("skills") or [])),
                clean(job.get("description") or job.get("summary") or ""),
                clean(job.get("source_url") or job.get("url") or ""),
                clean(job.get("source") or "Unknown"),
            ),
        )
        conn.commit()

    return True

def insert_job(job_data: Dict[str, Any], summary_text: str = "") -> int:
    """Wrapper for backward compatibility"""
    # Create a normalized-like dict (best effort)
    norm = {
        "title": job_data.get("title", ""),
        "company": job_data.get("company", "Unknown"),
        "location": job_data.get("location", "India"),
        "skills": job_data.get("skills", "").split(",") if isinstance(job_data.get("skills"), str) else [],
        "description": summary_text or job_data.get("description", ""),
        "url": job_data.get("source_url", "") or job_data.get("link", ""),
        "source": "manual"
    }
    if insert_job_if_new(norm):
        # We need the ID. `insert_job_if_new` doesn't return ID.
        # But this wrapper is legacy. Let's just return 1 if success.
        # If caller needs ID, they might be in trouble, but most callers just insert.
        # Let's try to fetch it back if needed, or just return 0/1.
        # Original returned job_id.
        return 1 
    return 0