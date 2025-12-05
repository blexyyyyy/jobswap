

from typing import List

from core.llm_client import CandidateProfile, JobPosting, generate_embedding

# ---------------------------------------------------------
# Helper: Convert candidate profile → clean text for embedding
# ---------------------------------------------------------

def candidate_to_embedding_text(candidate: CandidateProfile) -> str:
    """
    Convert a structured CandidateProfile into a clean, consistent
    text block that can be embedded. We only include fields that
    contribute to matching.
    """
    fields = [
        f"Summary: {candidate.summary}",
        f"Skills: {', '.join(candidate.skills)}",
        f"Experience: {candidate.experience}",
        f"Education: {candidate.education}"
    ]

    return "\n".join(fields).strip()


# ---------------------------------------------------------
# Helper: Convert job posting → clean text for embedding
# ---------------------------------------------------------

def job_to_embedding_text(job: JobPosting) -> str:
    """
    Convert a JobPosting into a clean embedding text. 
    This ensures consistent representation for vector search.
    """
    fields = [
        f"Title: {job.title}",
        f"Company: {job.company}",
        f"Location: {job.location}",
        f"Skills Required: {', '.join(job.skills)}",
        f"Description: {job.description}"
    ]

    return "\n".join(fields).strip()


# ---------------------------------------------------------
# Main functions
# ---------------------------------------------------------

def embed_candidate(candidate: CandidateProfile) -> List[float]:
    """
    Generate embedding for a candidate using the prepared text.
    """
    text = candidate_to_embedding_text(candidate)
    return generate_embedding(text)


def embed_job(job: JobPosting) -> List[float]:
    """
    Generate embedding for a job posting using the prepared text.
    """
    text = job_to_embedding_text(job)
    return generate_embedding(text)