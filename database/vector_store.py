import os
from typing import Any, Dict, List, Optional

import chromadb
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_store")


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