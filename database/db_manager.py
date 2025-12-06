"""Vector store helper (ChromaDB wrapper) and small DB helpers.

This module provides a thin `VectorStore` wrapper around ChromaDB used by
the project. It also contains a small helper to fetch candidate profiles
from the project's SQLite database.

Keeping a short module docstring satisfies linting and makes the purpose
clear when reading the file.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional

import chromadb
from dotenv import load_dotenv

load_dotenv()

# Path to persistent chroma directory
DEFAULT_CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_store")

# Path to the project's SQLite DB (used by the small helper below)
DB_PATH = os.getenv("DB_PATH", "database/jobmatcher.db")


class VectorStore:
    """
    Thin wrapper around ChromaDB for candidates and jobs.

    - Does NOT generate embeddings (that will be handled by matching/embeddings.py).
    - Only stores and queries embedding vectors.
    """

    def __init__(self, persist_directory: Optional[str] = None) -> None:
        self.persist_directory = persist_directory or DEFAULT_CHROMA_DIR
        os.makedirs(self.persist_directory, exist_ok=True)

        # Persistent client so data survives restarts
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # Two collections: one for candidates, one for jobs
        self.candidate_collection = self.client.get_or_create_collection(
            name="candidate_embeddings"
        )
        self.job_collection = self.client.get_or_create_collection(
            name="job_embeddings"
        )

    def add_candidates(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add candidate embeddings to the candidate collection.

        ids:         list of string IDs (typically candidate IDs from DB)
        embeddings:  list of embedding vectors (list of floats)
        metadatas:   optional list of metadata dicts
        """
        # Chroma type stubs are stricter than reality; we ignore arg-type here.
        self.candidate_collection.add(
            ids=ids,
            embeddings=embeddings,      # type: ignore[arg-type]
            metadatas=metadatas,        # type: ignore[arg-type]
        )

    def add_jobs(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add job embeddings to the job collection.

        ids:         list of string IDs (typically job IDs from DB)
        embeddings:  list of embedding vectors (list of floats)
        metadatas:   optional list of metadata dicts
        """
        self.job_collection.add(
            ids=ids,
            embeddings=embeddings,      # type: ignore[arg-type]
            metadatas=metadatas,        # type: ignore[arg-type]
        )

    def query_jobs_by_embedding(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Query the job collection by a single embedding vector.
        Returns top-N most similar jobs.
        """
        return self.job_collection.query(
            query_embeddings=[query_embedding],   # type: ignore[arg-type]
            n_results=n_results,
        )

    def query_candidates_by_embedding(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Query the candidate collection by a single embedding vector.
        Returns top-N most similar candidates.
        """
        return self.candidate_collection.query(
            query_embeddings=[query_embedding],   # type: ignore[arg-type]
            n_results=n_results,
        )

    def get_candidate_embedding(self, candidate_id: str) -> Optional[List[float]]:
        """
        Retrieve a stored candidate embedding by ID.
        Returns the embedding vector or None if not found.
        """
        result = self.candidate_collection.get(ids=[candidate_id], include=["embeddings"])
        if result and "embeddings" in result:
            embeddings = result["embeddings"]
            if embeddings is not None and len(embeddings) > 0:
                emb = embeddings[0]
                if emb is not None:
                    return list(emb)  # type: ignore[arg-type]
        return None

    def get_job_embedding(self, job_id: str) -> Optional[List[float]]:
        """
        Retrieve a stored job embedding by ID.
        Returns the embedding vector or None if not found.
        """
        result = self.job_collection.get(ids=[job_id], include=["embeddings"])
        if result and "embeddings" in result:
            embeddings = result["embeddings"]
            if embeddings is not None and len(embeddings) > 0:
                emb = embeddings[0]
                if emb is not None:
                    return list(emb)  # type: ignore[arg-type]
        return None
    

def get_candidate_profile(user_id: int) -> Optional[dict]:
    """Fetch candidate profile from SQLite DB by ID.

    This helper is intentionally small and self-contained so callers don't
    need to depend on a larger DB manager. It returns a dict or `None` if
    the candidate is not found.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    data = dict(row)
    # Convert comma-separated skill string to list
    if data.get("skills"):
        data["skills"] = [s.strip() for s in data["skills"].split(",")]
    else:
        data["skills"] = []

    return data


# ==========================================
# Job Insertion Helper
# ==========================================

def insert_job(job_data: Dict[str, Any], summary_text: str = "") -> int:
    """
    Insert a job into the database.
    Avoids duplicates based on source_url.
    """
    import sqlite3
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Helper to clean strings (remove null bytes)
    def clean(s):
        if isinstance(s, str):
            return s.replace('\x00', '')
        return s
    
    try:
        source = job_data.get("source_url", "")
        
        # Check if job exists
        if source:
            cursor.execute("SELECT id FROM jobs WHERE source_url = ?", (source,))
            existing = cursor.fetchone()
            if existing:
                return existing[0]
        
        # Use provided summary_text or fallbacks
        description = summary_text or job_data.get("description") or job_data.get("summary", "")
        
        cursor.execute("""
            INSERT INTO jobs (
                title, company, location, skills, description, 
                source_url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            clean(job_data.get("title")),
            clean(job_data.get("company")),
            clean(job_data.get("location")),
            clean(job_data.get("skills")),
            clean(description[:2000]), 
            clean(source)
        ))
        conn.commit()
        job_id = cursor.lastrowid
        return job_id
    except Exception as e:
        print(f"Error inserting job: {e}")
        raise e
    finally:
        conn.close()