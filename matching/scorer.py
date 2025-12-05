# matching/scorer.py

from typing import List, Tuple


def distance_to_similarity(distance: float) -> float:
    """
    Convert a Chroma distance (where lower = better)
    into a similarity score in [0, 1], where higher = better.

    Formula: similarity = 1 / (1 + distance)
    - distance = 0   → similarity = 1.0
    - distance = 1   → similarity = 0.5
    - distance = 3   → similarity = 0.25
    Simple, monotonic, and easy to reason about.
    """
    if distance < 0:
        # Just in case some weirdo negative value appears
        distance = 0.0
    return 1.0 / (1.0 + distance)


def score_matches(raw_matches: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """
    Take raw (job_id, distance) pairs from the matcher and convert them
    into (job_id, similarity_score) sorted by score DESC.

    Input:
        [(job_id, distance), ...]

    Output:
        [(job_id, score), ...] where score is in [0, 1]
    """
    scored: List[Tuple[int, float]] = []

    for job_id, distance in raw_matches:
        sim = distance_to_similarity(distance)
        scored.append((job_id, sim))

    # Sort by score descending (higher = better)
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored