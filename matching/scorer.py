# matching/scorer.py

from typing import Dict, List, Sequence, Optional , Any
import numpy as np
import pickle
import os

# Path where the trained ML model (e.g. LogisticRegression) will be stored.
# For now, if the file doesn't exist, we fall back to a heuristic.
MODEL_PATH = os.path.join("ml", "match_model.pkl")

# Global model object (loaded once)
MODEL: Optional[Any] = None

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            MODEL = pickle.load(f)
    except Exception:
        MODEL = None  # If loading fails, just fall back to heuristic
else:
    MODEL = None


# ---------------------------------------------------------
# BASIC UTILITIES
# ---------------------------------------------------------

def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """
    Compute cosine similarity between two 1D vectors.
    a, b can be list/tuple/ndarray of floats.
    """
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)

    denom = float(np.linalg.norm(a_arr) * np.linalg.norm(b_arr))
    if denom == 0.0:
        return 0.0

    num = float(a_arr @ b_arr)
    return num / denom


def skill_overlap(candidate_skills: List[str], job_skills: List[str]) -> float:
    """
    Return ratio of overlapping skills: |cand ∩ job| / |job|
    """
    if not job_skills:
        return 0.0
    return len(set(candidate_skills) & set(job_skills)) / len(job_skills)


# ---------------------------------------------------------
# ML FEATURE BUILDER
# ---------------------------------------------------------

def build_features(
    candidate: Dict,
    job: Dict,
    cand_vec: Sequence[float],
    job_vec: Sequence[float],
) -> Dict[str, float]:
    """
    Extract structured features for the ML model.
    Expects:
      candidate: dict with keys like "skills", "experience_years", "location"
      job:       dict with keys like "skills", "min_experience", "location"
      cand_vec, job_vec: embedding vectors (same dimension)
    """
    features: Dict[str, float] = {}

    features["semantic_sim"] = cosine_similarity(cand_vec, job_vec)
    features["skill_overlap"] = skill_overlap(
        candidate.get("skills", []),
        job.get("skills", []),
    )

    cand_exp = float(candidate.get("experience_years", 0) or 0)
    job_min_exp = float(job.get("min_experience", 0) or 0)
    features["exp_gap"] = cand_exp - job_min_exp

    features["location_match"] = float(
        1.0 if candidate.get("location") == job.get("location") else 0.0
    )

    return features


FEATURE_ORDER = ["semantic_sim", "skill_overlap", "exp_gap", "location_match"]


# ---------------------------------------------------------
# ML SCORING ENGINE
# ---------------------------------------------------------

def ml_predict_probability(features: Dict[str, float]) -> float:
    """
    Predict match probability using trained ML model.
    Falls back to a simple heuristic if model isn't available.
    """
    # If we don't have a trained model yet, use a heuristic
    if MODEL is None:
        # 70% weight on semantic similarity, 30% on skill overlap
        return (
            features.get("semantic_sim", 0.0) * 0.7
            + features.get("skill_overlap", 0.0) * 0.3
        )

    # Build feature vector in consistent order
    x = [[features[f] for f in FEATURE_ORDER]]
    # We expect model to have predict_proba
    proba = MODEL.predict_proba(x)[0][1]
    return float(proba)


def classify_match(prob: float) -> str:
    """
    Convert probability in [0,1] into a human-readable label.
    """
    if prob >= 0.75:
        return "Excellent"
    elif prob >= 0.40:
        return "Potential"
    else:
        return "Challenging"


# ---------------------------------------------------------
# FINAL SCORING PIPELINE
# ---------------------------------------------------------

def score_job(
    candidate: Dict,
    job: Dict,
    cand_vec: Sequence[float],
    job_vec: Sequence[float],
) -> Dict[str, object]:
    """
    Main scoring entry point.

    Returns a dict:
        {
            "probability": float,          # 0–1
            "label": "Excellent|Potential|Challenging",
            "features": {
                "semantic_sim": float,
                "skill_overlap": float,
                "exp_gap": float,
                "location_match": float
            }
        }
    """
    features = build_features(candidate, job, cand_vec, job_vec)
    prob = ml_predict_probability(features)
    label = classify_match(prob)

    return {
        "probability": prob,
        "label": label,
        "features": features,
    }