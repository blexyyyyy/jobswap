# ml/build_dataset.py
from __future__ import annotations

from typing import Optional

import pandas as pd

from database.connection import get_db_connection
from ml.features import extract_job_features


def _row_to_user(row) -> dict:
    return {
        "skills": row["user_skills"],
        "preferred_location": row["user_preferred_location"],
        "preferred_seniority": row["user_preferred_seniority"],
    }


def _row_to_job(row) -> dict:
    return {
        "title": row["job_title"],
        "company": row["job_company"],
        "location": row["job_location"],
        "skills": row["job_skills"],
        "description": row["job_description"],
    }


def build_dataset() -> pd.DataFrame:
    """
    Build a supervised dataset from user_swipes + users + jobs.

    Label:
        1 = positive (apply/save)
        0 = negative (skip)
    """
    with get_db_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT
                us.user_id,
                us.job_id,
                us.action,
                u.skills              AS user_skills,
                u.preferred_location  AS user_preferred_location,
                u.preferred_seniority AS user_preferred_seniority,
                j.title               AS job_title,
                j.company             AS job_company,
                j.location            AS job_location,
                j.skills              AS job_skills,
                j.description         AS job_description
            FROM user_swipes us
            JOIN users u ON us.user_id = u.id
            JOIN jobs j  ON us.job_id = j.id
            WHERE us.action IN ('apply', 'save', 'skip')
            """,
            conn,
        )

    if df.empty:
        return df  # empty

    rows = []
    for _, row in df.iterrows():
        user = _row_to_user(row)
        job = _row_to_job(row)
        feats = extract_job_features(user, job)

        label = 1 if row["action"] in ("apply", "save") else 0
        feats["label"] = label
        rows.append(feats)

    return pd.DataFrame(rows)