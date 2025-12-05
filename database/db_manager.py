import os
import sqlite3
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_PATH = os.getenv("DB_PATH", "database/jobmatcher.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Return a SQLite connection with row factory enabled."""
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(schema_path: str = "database/schema.sql", db_path: Optional[str] = None) -> None:
    """Initialize the database using schema.sql."""
    path = db_path or DEFAULT_DB_PATH
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with get_connection(path) as conn, open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
        conn.executescript(schema)
        conn.commit()


def insert_candidate(profile: Dict[str, Any], raw_text: str, db_path: Optional[str] = None) -> int | None:
    """
    Insert a parsed candidate profile into the DB.
    Expects keys: name, email, phone, summary, skills, experience, education
    """
    path = db_path or DEFAULT_DB_PATH

    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO candidates (name, email, phone, summary, skills, experience, education, raw_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile.get("name"),
                profile.get("email"),
                profile.get("phone"),
                profile.get("summary"),
                profile.get("skills"),       # can be JSON string later
                profile.get("experience"),
                profile.get("education"),
                raw_text,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def insert_job(job: Dict[str, Any], raw_text: str, db_path: Optional[str] = None) -> Optional[int]:

    """
    Insert a parsed job posting into the DB.
    Expects keys: title, company, location, seniority, skills, description
    """
    path = db_path or DEFAULT_DB_PATH

    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jobs (title, company, location, seniority, skills, description, raw_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.get("title"),
                job.get("company"),
                job.get("location"),
                job.get("seniority"),
                job.get("skills"),
                job.get("description"),
                raw_text,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def check_duplicate_job(title: str, company: str, location: str, db_path: Optional[str] = None) -> bool:
    """Check if a job already exists."""
    path = db_path or DEFAULT_DB_PATH
    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM jobs WHERE title = ? AND company = ? AND location = ?",
            (title, company, location),
        )
        return cursor.fetchone() is not None
