# ml/model.py
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Optional, Dict

from ml.features import extract_job_features, as_vector

MODEL_PATH = Path("ml/models/logreg_job_match.pkl")

_MODEL_CACHE = None
_FEATURE_ORDER = None

def clear_cache():
    """
    Clear the in-memory model cache.
    Useful after retraining to force reload.
    """
    global _MODEL_CACHE, _FEATURE_ORDER
    _MODEL_CACHE = None
    _FEATURE_ORDER = None
    print("[ML] Model cache cleared.")


def load_model():
    """
    Load the trained model and feature order from disk.
    Cached in memory.
    """
    global _MODEL_CACHE, _FEATURE_ORDER
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE, _FEATURE_ORDER

    if not MODEL_PATH.exists():
        return None, None

    try:
        with MODEL_PATH.open("rb") as f:
            data = pickle.load(f)
            _MODEL_CACHE = data["model"]
            _FEATURE_ORDER = data["feature_order"]
            print(f"[ML] Model loaded from {MODEL_PATH}")
            return _MODEL_CACHE, _FEATURE_ORDER
    except Exception as e:
        print(f"[ML] Error loading model: {e}")
        return None, None


def score_job(user: Dict, job: Dict) -> float:
    """
    Predict match probability for a (user, job) pair.
    Returns float 0.0 to 1.0.
    """
    clf, feature_order = load_model()
    
    # Extract features
    feats = extract_job_features(user, job)
    
    # If no model, return heuristic fallback or 0.5
    if clf is None:
        # Fallback: normalize skill overlap to roughly 0.5-0.9 range?
        # Or just return 0.5 neutral
        return 0.5

    # Align features with model's expected order
    # (The model was trained with a specific column order)
    # We must construct vector in that exact order
    try:
        # We need to ensure logic matches build_dataset.py
        # extract_job_features returns dict. 
        # But we need to order it by feature_order loaded from pkl
        vector = [feats.get(k, 0.0) for k in feature_order]
        
        # Predict probability of class 1
        # reshape(1, -1) because single sample
        proba = clf.predict_proba([vector])[0][1]
        return float(proba)
    except Exception as e:
        print(f"[ML] scoring error: {e}")
        return 0.5