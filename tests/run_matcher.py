#!/usr/bin/env python3
"""Complete matcher workflow - parse, embed, store, and match."""

from core.llm_client import extract_resume_structured
from database.vector_store import VectorStore
from matching.embeddings import embed_candidate
from matching.matcher import get_top_k_jobs

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

print("\n--- PARSE + EMBED ---")
cand = extract_resume_structured(resume_text)
c_vec = embed_candidate(cand)
print(f"✅ Candidate: {cand.name}")
print(f"✅ Candidate embedding length: {len(c_vec)}")

print("\n--- STORE CANDIDATE IN CHROMA ---")
vs = VectorStore()
vs.add_candidates(
    ids=["1"],
    embeddings=[c_vec],
    metadatas=[{"name": cand.name}],
)
print("✅ Stored candidate 1")

print("\n--- MATCHING ---")
matches = get_top_k_jobs(candidate_id=1, k=5)
print(f"✅ Top {len(matches)} matching jobs:")
for job_id, score in matches:
    print(f"   - Job ID {job_id}: similarity {score:.4f}")

print("\n✅ Complete!")
