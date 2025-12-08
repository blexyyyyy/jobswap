from typing import List, Dict
import re

from scrapers.base import RawJob, clean_text


SENIORITY_KEYWORDS = {
    "intern": ["intern", "internship", "trainee"],
    "junior": ["junior", "jr."],
    "mid": ["mid-level", "mid level", "associate"],
    "senior": ["senior", "sr.", "lead"],
    "manager": ["manager", "head", "director"],
}


def extract_skills_from_text(text: str) -> List[str]:
    """Very dumb skill extraction. Later we replace with ML/NER."""
    text_lower = text.lower()
    known_skills = [
        "python", "java", "javascript", "react", "node",
        "sql", "mongo", "docker", "kubernetes", "aws",
        "gcp", "azure", "ml", "machine learning", "nlp",
        "pandas", "numpy", "django", "flask",
    ]
    found = []
    for skill in known_skills:
        if skill in text_lower:
            found.append(skill)
    return sorted(set(found))


def normalize_location(raw_location: str) -> str:
    if not raw_location:
        return "India"  # sensible default for you
    return clean_text(raw_location)


def normalize_seniority(title: str) -> str:
    title_lower = title.lower()
    for level, keywords in SENIORITY_KEYWORDS.items():
        if any(k in title_lower for k in keywords):
            return level
    return "unspecified"


def normalize_raw_job(job: RawJob) -> Dict:
    """
    Returns a dict that matches your DB + is easy to map to JobOut.
    """
    title = clean_text(job.title)
    company = clean_text(job.company)
    desc = clean_text(job.description or job.raw_text)

    skills = job.skills or extract_skills_from_text(desc + " " + title)
    skills = sorted(set(s.strip() for s in skills if s.strip()))

    location = normalize_location(job.location)

    return {
        "title": title,
        "company": company or "Unknown",
        "location": location,
        "skills": skills,
        "description": desc,
        "url": job.url,
        "raw_text": job.raw_text or desc,
        "source": job.source,
        "seniority": normalize_seniority(title),
    }
