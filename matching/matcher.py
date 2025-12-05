from typing import List, Tuple

from database.vector_store import VectorStore

TOP_K = 5


def get_top_k_jobs(candidate_id: int, k: int = TOP_K) -> List[Tuple[int, float]]:
    """
    Given a candidate ID (from the DB), fetch the candidate embedding from Chroma,
    run a similarity search against job embeddings, and return the top K job IDs
    with similarity scores.

    Output format:
        [
            (job_id, score),
            (job_id, score),
            ...
        ]
    """
    vs = VectorStore()

    # 1️⃣ Fetch candidate embedding from Chroma
    candidate_vector = vs.get_candidate_embedding(str(candidate_id))
    if candidate_vector is None:
        raise ValueError(f"No embedding found for candidate ID {candidate_id}")

    # 2️⃣ Query job embeddings with this candidate vector
    result = vs.query_jobs_by_embedding(
        query_embedding=candidate_vector,
        n_results=k,
    )

    ids_lists = result.get("ids", [])
    scores_lists = result.get("distances", [])

    if not ids_lists or not scores_lists:
        return []

    ids = ids_lists[0]
    scores = scores_lists[0]

    top_jobs: List[Tuple[int, float]] = []
    for job_id, score in zip(ids, scores):
        top_jobs.append((int(job_id), float(score)))

    return top_jobs