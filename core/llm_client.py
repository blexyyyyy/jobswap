import json
import os
import time
from typing import Any, Dict, List

from dotenv import load_dotenv
# --- New SDK Imports ---
from google import genai
from google.genai import types
from pydantic import BaseModel

# --------------------------
# Load API Key & Setup Client
# --------------------------

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing in .env")

# Initialize the Client (instead of genai.configure)
client = genai.Client(api_key=API_KEY)

GEMINI_MODEL = "gemini-2.5-flash"
EMBED_MODEL = "text-embedding-004"


# --------------------------
# Pydantic Schemas
# --------------------------

class CandidateProfile(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: List[str] = []
    experience: str = ""
    education: str = ""
    raw_text: str = ""
    location: str = ""



class JobPosting(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    seniority: str = ""
    skills: List[str] = []
    description: str = ""


# --------------------------
# JSON Helper
# --------------------------

def _call_gemini_json(prompt: str) -> Dict[str, Any]:
    """Force Gemini to return JSON using the NEW SDK."""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )

            # 🛑 FIX: Check for None before stripping (Pylance safety check)
            if not response.text:
                print(f"[Gemini JSON WARNING] Attempt {attempt+1}: Empty response (Safety filter?)")
                continue

            text = response.text.strip()
            
            # Clean up potential markdown formatting
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            elif text.startswith("```"):
                text = text.replace("```", "").strip()
            
            return json.loads(text)

        except Exception as e:
            print(f"[Gemini JSON ERROR] Attempt {attempt+1}/3 -> {e}")
            time.sleep(1)

    raise RuntimeError("Gemini JSON generation failed after 3 attempts.")


# --------------------------
# Resume / Job Parsing
# --------------------------

def extract_resume_structured(raw_text: str) -> CandidateProfile:
    prompt = f"""
    SYSTEM: Extract structured data from this resume.
    Return ONLY valid JSON matching this schema:
    {{
        "name": "str", "email": "str", "phone": "str", "summary": "str", 
        "skills": ["str"], "experience": "str", "education": "str"
    }}

    Resume:
    {raw_text}
    """
    data = _call_gemini_json(prompt)
    return CandidateProfile(**data)


def extract_job_structured(raw_text: str) -> JobPosting:
    prompt = f"""
    SYSTEM: Extract structured data from this job posting.
    Return ONLY valid JSON matching this schema:
    {{
        "title": "str", "company": "str", "location": "str", "seniority": "str", 
        "skills": ["str"], "description": "str"
    }}

    Job posting:
    {raw_text}
    """
    data = _call_gemini_json(prompt)
    return JobPosting(**data)


# --------------------------
# Embeddings
# --------------------------

def generate_embedding(text: str) -> List[float]:
    if not text:
        return []

    try:
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text
        )
        
        # 🛑 FIX: Explicitly check for embeddings list validity (Pylance safety check)
        if result.embeddings and len(result.embeddings) > 0:
            values = result.embeddings[0].values
            if values:
                return values
                
        return []

    except Exception as e:
        print(f"[Embedding ERROR] {e}")
        return []


# --------------------------
# Explanation (FINAL CORRECTED VERSION)
# --------------------------

# 🛑 FIX: This should be the ONLY definition of explain_match
def explain_match(candidate: CandidateProfile, job: JobPosting, score: float) -> str:
    prompt = f"""
    Explain the match between the following candidate and job.
    Use 4–6 sentences. Be clear and honest.

    Candidate:
    {candidate.model_dump_json(indent=2)}

    Job:
    {job.model_dump_json(indent=2)}

    Score: {score}
    """
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )
        
        # 🛑 FIX: Return a fallback string if response.text is None
        if not response.text:
            return "No explanation available (Model returned empty response)."
            
        return response.text.strip()

    except Exception as e:
        return f"[Explanation ERROR] {e}"


# --------------------------
# Debug Test
# --------------------------

if __name__ == "__main__":
    print("Testing Gemini Client (New SDK)...\n")

    # Use fuller text for better extraction tests
    test_resume = """
    Veerat Matey
    Email: veerat@example.com
    Phone: +91 9999999999
    Summary: 5 years experience as a Python developer with focus on backend REST APIs and Linux server management.
    Skills: Python, Linux, FastAPI, PostgreSQL, AWS, Product Strategy
    Experience: Worked at Nirvaan as a sales executive (2018-2020) and then TechCorp as a Senior Python Engineer (2020-Present).
    Education: B.Tech in Computer Science from IIT Delhi.
    """

    test_job = """
    Hiring: Senior Python Developer
    Company: Stellar Solutions
    Location: Remote
    Seniority: Senior
    Skills: Python, FastAPI, AWS, CI/CD, Linux, Docker
    Description: We are seeking a highly experienced backend Python engineer to lead API development and deployment on AWS infrastructure.
    """

    print("--- Extracting Resume ---")
    r = extract_resume_structured(test_resume)
    print(r.model_dump_json(indent=2))

    print("\n--- Extracting Job ---")
    j = extract_job_structured(test_job)
    print(j.model_dump_json(indent=2))

    print("\n--- Generating Embedding ---")
    emb = generate_embedding(r.summary)
    print(f"Embedding dimensions: {len(emb)}")

    print("\n--- Explaining Match ---")
    print(explain_match(r, j, 0.92))