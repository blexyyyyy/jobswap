# matching/scorer.py

from typing import Dict, List

import joblib
import numpy as np

MODEL_PATH = "ml/match_model.pkl"

# Try loading the ML model; fallback to None if not trained yet
try:
    MODEL = joblib.load(MODEL_PATH)
except:
    MODEL = None


# ---------------------------------------------------------
# BASIC UTILITIES
# ---------------------------------------------------------

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a = np.array(a)
    b = np.array(b)
    return float(a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def skill_overlap(candidate_skills: List[str], job_skills: List[str]) -> float:
    """Return ratio of overlapping skills."""
    if not job_skills:
        return 0.0
    return len(set(candidate_skills) & set(job_skills)) / len(job_skills)


# ---------------------------------------------------------
# ML FEATURE BUILDER
# ---------------------------------------------------------

def build_features(candidate: dict, job: dict, cand_vec: List[float], job_vec: List[float]) -> Dict:
    """Extract structured features used by the ML model."""
    
    features = {
        "semantic_sim": cosine_similarity(cand_vec, job_vec),
        "skill_overlap": skill_overlap(candidate.get("skills", []), job.get("skills", [])),
        "exp_gap": candidate.get("experience_years", 0) - job.get("min_experience", 0),
        "location_match": int(candidate.get("location") == job.get("location")),
    }

    return features


FEATURE_ORDER = ["semantic_sim", "skill_overlap", "exp_gap", "location_match"]


# ---------------------------------------------------------
# ML SCORING ENGINE
# ---------------------------------------------------------

def ml_predict_probability(features: Dict) -> float:
    """
    Predict match probability using trained ML model.
    Falls back to simple heuristic if model is missing.
    """
    if MODEL is None:
        # fallback if ML model is not trained yet
        return features["semantic_sim"] * 0.7 + features["skill_overlap"] * 0.3

    x = [[features[f] for f in FEATURE_ORDER]]
    return float(MODEL.predict_proba(x)[0][1])


def classify_match(prob: float) -> str:
    """Convert probability → label."""
    if prob >= 0.75:
        return "Excellent"
    elif prob >= 0.40:
        return "Potential"
    else:
        return "Challenging"


# ---------------------------------------------------------
# FINAL SCORING PIPELINE
# ---------------------------------------------------------

def score_job(candidate: dict, job: dict, cand_vec: List[float], job_vec: List[float]) -> Dict:
    """
    Main scoring entry point.

    Returns:
        {
            "probability": float,
            "label": "Excellent/Potential/Challenging",
            "features": {...}
        }
    """
    features = build_features(candidate, job, cand_vec, job_vec)
    prob = ml_predict_probability(features)
    label = classify_match(prob)

    return {
        "probability": prob,
        "label": label,
        "features": features
    }