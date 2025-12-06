# matching/api_layer.py

import sqlite3
from typing import Dict, List

from app.main import DB_PATH  # reuse your existing DB path
from core.llm_client import CandidateProfile, JobPosting
from matching.embeddings import embed_candidate, embed_job
from matching.scorer import (build_features,  # we already defined these
                             score_job)


class MatchingAPI:
    """
    Service layer for job matching logic.

    FastAPI routes should call this instead of doing:
    - raw sqlite
    - embeddings
    - manual feature logic
    directly in the route handler.
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path

    def _get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # --------- Helpers to build models ---------

    def _build_candidate_from_user(self, user: Dict) -> CandidateProfile:
        return CandidateProfile(
            name=user.get("name") or "",
            email=user["email"],
            phone=user.get("phone") or "",
            summary=user.get("resume_text") or "",
            skills=[s.strip() for s in (user.get("skills") or "").split(",")] if user.get("skills") else [],
            experience=str(user.get("experience_years") or ""),
            education="",
            raw_text=user.get("resume_text") or "",
            location=user.get("preferred_location") or "",
        )

    def _build_job_from_row(self, row: Dict) -> JobPosting:
        return JobPosting(
            title=row.get("title") or "",
            company=row.get("company") or "",
            location=row.get("location") or "",
            seniority=row.get("seniority") or "",
            skills=[s.strip() for s in (row.get("skills") or "").split(",")] if row.get("skills") else [],
            description=row.get("description") or "",
        )

    # --------- Public API: Job Feed ---------

    def get_job_feed_for_user(self, user: Dict, limit: int = 20) -> List[Dict]:
        """
        Returns a list of jobs enriched with ML scores:
        - match_probability
        - match_label
        - ML features
        (No LLM explanation here yet – we’ll add that later cleanly.)
        """
        conn = self._get_db()
        cur = conn.cursor()

        # 1) Fetch jobs user hasn’t swiped
        cur.execute(
            """
            SELECT j.*
            FROM jobs j
            WHERE j.id NOT IN (
                SELECT job_id FROM user_swipes WHERE user_id = ?
            )
            ORDER BY j.created_at DESC
            LIMIT ?
            """,
            (user["id"], limit),
        )
        job_rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        if not job_rows:
            return []

        # 2) Build candidate + embedding once
        candidate = self._build_candidate_from_user(user)
        cand_vec = embed_candidate(candidate)

        enriched: List[Dict] = []

        for jr in job_rows:
            job = self._build_job_from_row(jr)
            job_vec = embed_job(job)

            cand_dict: Dict[str, object] = {
                "skills": candidate.skills,
                "experience_years": user.get("experience_years") or 0,
                "location": candidate.location,
            }
            job_dict: Dict[str, object] = {
                "skills": job.skills,
                "min_experience": 0,  # TODO: use real field when you add it
                "location": job.location,
            }

            features = build_features(
                candidate=cand_dict,
                job=job_dict,
                cand_vec=cand_vec,
                job_vec=job_vec,
            )
            scored = score_job(
                candidate=cand_dict,
                job=job_dict,
                cand_vec=cand_vec,
                job_vec=job_vec,
            )

            enriched.append(
                {
                    **jr,
                    "skills": job.skills,
                    "match_probability": scored["probability"],
                    "match_label": scored["label"],
                    "match_features": scored["features"],
                }
            )

        # 3) Sort by ML probability (best first)
        enriched.sort(key=lambda x: x["match_probability"], reverse=True)

        return enriched

    # --------- Public API: Swipe Logging ---------

    def record_swipe_and_log_interaction(self, user: Dict, job_id: int, action: str) -> None:
        """
        - Stores swipe in user_swipes
        - Logs ML features in interactions table
        """
        if action not in ("apply", "save", "skip"):
            raise ValueError("Invalid action")

        conn = self._get_db()
        cur = conn.cursor()

        # 1) Store / update swipe
        cur.execute(
            """
            INSERT OR REPLACE INTO user_swipes (user_id, job_id, action)
            VALUES (?, ?, ?)
            """,
            (user["id"], job_id, action),
        )

        # 2) Fetch job row
        cur.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cur.fetchone()
        if not row:
            conn.commit()
            conn.close()
            raise ValueError("Job not found")

        job_row = dict(row)
        candidate = self._build_candidate_from_user(user)
        job = self._build_job_from_row(job_row)

        cand_vec = embed_candidate(candidate)
        job_vec = embed_job(job)

        cand_dict: Dict[str, object] = {
            "skills": candidate.skills,
            "experience_years": user.get("experience_years") or 0,
            "location": candidate.location,
        }
        job_dict: Dict[str, object] = {
            "skills": job.skills,
            "min_experience": 0,
            "location": job.location,
        }

        features = build_features(
            candidate=cand_dict,
            job=job_dict,
            cand_vec=cand_vec,
            job_vec=job_vec,
        )

        label = 1 if action in ("apply", "save") else 0

        # 3) Insert into interactions
        cur.execute(
            """
            INSERT INTO interactions (
                user_id,
                job_id,
                semantic_sim,
                skill_overlap,
                exp_gap,
                location_match,
                label
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                job_id,
                float(features.get("semantic_sim", 0.0)),
                float(features.get("skill_overlap", 0.0)),
                float(features.get("exp_gap", 0.0)),
                float(features.get("location_match", 0.0)),
                int(label),
            ),
        )

        conn.commit()
        conn.close()
