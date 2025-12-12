# ml/features.py
from __future__ import annotations

from typing import Dict, List, Set, Optional
import math


def _parse_skills(value: Optional[str | List[str]]) -> Set[str]:
    """
    Convert skills from comma-separated string or list into a clean lowercased set.
    """
    if value is None:
        return set()

    if isinstance(value, list):
        raw = value
    else:
        raw = str(value).split(",")

    return {
        s.strip().lower()
        for s in raw
        if isinstance(s, str) and s.strip()
    }


def _norm(s: Optional[str]) -> str:
    return " ".join(str(s or "").split()).lower()


FEATURE_KEYS: List[str] = [
    "skill_overlap",
    "skill_jaccard",
    "location_match",
    "seniority_match",
    "title_keyword_match",
    "description_length",
    "title_length",
]


def extract_job_features(user: Dict, job: Dict) -> Dict[str, float]:
    """
    Extract numeric features for (user, job) pair.

    Expected user keys:
        - skills (comma string or list)
        - preferred_location (str or None)
        - preferred_seniority (str or None)

    Expected job keys:
        - title
        - company
        - location
        - skills (comma string or list)
        - description
    """
    user_skills = _parse_skills(user.get("skills"))
    job_skills = _parse_skills(job.get("skills"))

    # 1) Skill overlap
    if user_skills and job_skills:
        overlap = len(user_skills & job_skills)
        union = len(user_skills | job_skills)
        jaccard = overlap / union if union > 0 else 0.0
    else:
        overlap = 0
        jaccard = 0.0

    # 2) Location match
    user_loc = _norm(user.get("preferred_location"))
    job_loc = _norm(job.get("location"))
    location_match = 1.0 if user_loc and user_loc in job_loc else 0.0

    # 3) Seniority match
    user_sen = _norm(user.get("preferred_seniority"))
    title = _norm(job.get("title"))
    seniority_match = 1.0 if user_sen and user_sen in title else 0.0

    # 4) Title keywords vs skills
    title_keyword_match = 0.0
    if title and user_skills:
        for skill in user_skills:
            if skill and skill in title:
                title_keyword_match = 1.0
                break

    # 5) Text lengths
    desc = job.get("description") or ""
    desc_len = len(desc)
    title_len = len(job.get("title") or "")

    features: Dict[str, float] = {
        "skill_overlap": float(overlap),
        "skill_jaccard": float(jaccard),
        "location_match": float(location_match),
        "seniority_match": float(seniority_match),
        "title_keyword_match": float(title_keyword_match),
        "description_length": float(min(desc_len, 5000)),
        "title_length": float(min(title_len, 200)),
    }

    # Ensure all FEATURE_KEYS exist
    for key in FEATURE_KEYS:
        features.setdefault(key, 0.0)

    return features


def as_vector(features: Dict[str, float]) -> List[float]:
    """
    Convert feature dict into ordered list matching FEATURE_KEYS.
    """
    return [float(features.get(name, 0.0)) for name in FEATURE_KEYS]