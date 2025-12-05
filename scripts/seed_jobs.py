from typing import Any, Dict, List

from core.llm_client import generate_embedding
from database.db_manager import insert_job
from database.vector_store import VectorStore
from parsers.job_parser import parse_job_text

# -----------------------------
# Sample Job Postings
# -----------------------------

SAMPLE_JOBS: List[Dict[str, str]] = [
    {
        "id": "job_python_backend",
        "text": """
        Hiring: Python Backend Developer
        Company: DataFlow Systems
        Location: Remote
        Seniority: Mid-Level

        Responsibilities:
        - Build and maintain REST APIs using FastAPI or Django.
        - Work with PostgreSQL and Redis.
        - Deploy and monitor services on Linux servers.

        Skills:
        - Python, FastAPI or Django, SQL, Linux, Docker.
        - Experience with background jobs and Celery is a plus.
        """
    },
    {
        "id": "job_ml_engineer",
        "text": """
        Role: Machine Learning Engineer
        Company: Insight Analytics
        Location: Bangalore (Hybrid)
        Seniority: Mid to Senior

        Job Description:
        - Build and deploy ML models for prediction and recommendation.
        - Work with Python, scikit-learn, and basic deep learning.
        - Collaborate with data engineering and product teams.

        Required Skills:
        - Python, pandas, scikit-learn, basic statistics.
        - Experience with model deployment (FastAPI, Flask) is a bonus.
        """
    },
    {
        "id": "job_data_analyst",
        "text": """
        Position: Data Analyst
        Company: FinEdge Solutions
        Location: Mumbai (On-site)
        Seniority: Junior

        Responsibilities:
        - Create dashboards and reports for business stakeholders.
        - Clean and analyze data using SQL and Excel.
        - Work with Python and visualization tools.

        Skills:
        - SQL, Excel, Python, basic statistics.
        - Knowledge of Power BI or Tableau is preferred.
        """
    },
    {
        "id": "job_devops_engineer",
        "text": """
        Title: DevOps Engineer
        Company: CloudNova
        Location: Remote
        Seniority: Mid-Level

        Responsibilities:
        - Manage CI/CD pipelines and cloud infrastructure.
        - Work with Docker, Kubernetes, and monitoring tools.
        - Collaborate with development teams to improve deployment workflows.

        Skills:
        - Linux, Docker, CI/CD (GitHub Actions, GitLab CI), Kubernetes.
        - Experience with AWS or GCP is a plus.
        """
    },
    {
        "id": "job_sales_engineer",
        "text": """
        Role: Sales Engineer (SaaS)
        Company: GrowthStack
        Location: Remote (India)
        Seniority: Junior to Mid

        Job Description:
        - Work with the sales team to close technical deals.
        - Understand client requirements and demo the product.
        - Coordinate with engineering to handle custom requests.

        Required Skills:
        - Strong communication and presentation.
        - Basic understanding of APIs and web applications.
        - Previous experience in B2B SaaS is an advantage.
        """
    },
]


# -----------------------------
# Helper: Build text for embedding
# -----------------------------

def build_job_embedding_text(job_struct: Dict[str, Any]) -> str:
    """
    Concatenate the most relevant fields into a single text string
    for embedding generation.
    """
    title = job_struct.get("title", "")
    company = job_struct.get("company", "")
    location = job_struct.get("location", "")
    seniority = job_struct.get("seniority", "")
    skills = job_struct.get("skills", [])
    description = job_struct.get("description", "")

    if isinstance(skills, list):
        skills_text = ", ".join(skills)
    else:
        skills_text = str(skills)

    parts = [
        title,
        company,
        location,
        seniority,
        skills_text,
        description,
    ]
    return "\n".join([p for p in parts if p])


# -----------------------------
# Main seeding logic
# -----------------------------

def seed_jobs() -> None:
    vector_store = VectorStore()

    for job in SAMPLE_JOBS:
        job_id_label = job["id"]
        raw_text = job["text"].strip()

        print(f"\n⚙️ Processing job: {job_id_label}")

        # 1. Parse job posting with LLM
        parsed = parse_job_text(raw_text)
        parsed_dict = parsed.model_dump()

        # 2. Prepare dict for DB (convert skills list -> string)
        db_payload = {
            "title": parsed_dict.get("title", ""),
            "company": parsed_dict.get("company", ""),
            "location": parsed_dict.get("location", ""),
            "seniority": parsed_dict.get("seniority", ""),
            "skills": ", ".join(parsed_dict.get("skills", [])) if isinstance(parsed_dict.get("skills"), list) else str(parsed_dict.get("skills", "")),
            "description": parsed_dict.get("description", ""),
        }

        # 3. Insert into SQLite
        job_db_id = insert_job(db_payload, raw_text)
        if job_db_id is None:
            print(f"❌ Failed to insert job {job_id_label} into DB, skipping embedding.")
            continue

        print(f"✅ Inserted into DB with id={job_db_id}")

        # 4. Generate embedding
        embed_text = build_job_embedding_text(parsed_dict)
        embedding = generate_embedding(embed_text)

        if not embedding:
            print(f"❌ No embedding generated for job {job_id_label}, skipping Chroma.")
            continue

        # 5. Store embedding in Chroma
        vector_store.add_jobs(
            ids=[str(job_db_id)],
            embeddings=[embedding],
            metadatas=[{
                "db_id": job_db_id,
                "label_id": job_id_label,
                "title": db_payload["title"],
                "company": db_payload["company"],
                "location": db_payload["location"],
                "seniority": db_payload["seniority"],
            }],
        )

        print(f"✅ Stored embedding in Chroma for job id={job_db_id}")


if __name__ == "__main__":
    seed_jobs()
    print("\n🎉 Job seeding complete.")