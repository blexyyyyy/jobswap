# scripts/test_matching.py

from core.llm_client import extract_resume_structured
from database.vector_store import VectorStore
from matching.embeddings import embed_candidate
from matching.matcher import get_top_k_jobs
from matching.scorer import score_matches


def main() -> None:
    # 1) Sample resume (later you can load from file)
    resume_text = """
    Amit Sharma
    Email: amit.sharma@example.com
    Phone: +91 9876543210

    Summary:
    Python developer with 3 years of experience building backend systems.
    Strong knowledge of APIs, automation, and data processing.

    Skills:
    Python, FastAPI, SQL, Linux, Docker

    Experience:
    Backend Developer at CodeWorks (2021–2024)
    Worked on REST APIs, automation tools, and data pipelines.

    Education:
    B.Tech in Computer Science
    """

    print("\n--- 1. PARSE RESUME ---")
    candidate = extract_resume_structured(resume_text)
    print("Name:", candidate.name)
    print("Skills:", candidate.skills)

    # 2) Embed candidate
    print("\n--- 2. GENERATE EMBEDDING ---")
    cand_vec = embed_candidate(candidate)
    print("Candidate embedding length:", len(cand_vec))

    # 3) Store candidate embedding in Chroma
    print("\n--- 3. STORE CANDIDATE IN CHROMA ---")
    vector_store = VectorStore()
    candidate_id = "1"  # for now, fixed ID for testing
    vector_store.add_candidates(
        ids=[candidate_id],
        embeddings=[cand_vec],
        metadatas=[{"name": candidate.name}],
    )
    print(f"Stored candidate embedding with id={candidate_id}")

    # 4) Run matcher to get raw distances
    print("\n--- 4. RAW MATCHING (DISTANCES) ---")
    raw_matches = get_top_k_jobs(candidate_id=int(candidate_id), k=5)
    print("Raw matches (job_id, distance):", raw_matches)

    # 5) Convert distances -> similarity scores [0, 1]
    print("\n--- 5. SCORED MATCHES (SIMILARITY) ---")
    scored_matches = score_matches(raw_matches)
    for job_id, score in scored_matches:
        print(f"Job ID: {job_id} | Score: {score:.3f}")

    print("\n✅ Test completed.")


if __name__ == "__main__":
    main()