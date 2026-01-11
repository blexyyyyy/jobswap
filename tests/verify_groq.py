
import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()
print(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")

try:
    from matching.explanations import explanation_generator
    print("[OK] Successfully imported explanation_generator")
except Exception as e:
    print(f"[X] Failed to import explanation_generator: {ascii(e)}")
    sys.exit(1)

# Mock data
candidate = {
    "skills": ["python", "fastapi"],
    "experience_years": 5,
    "preferred_location": "Remote",
    "preferred_seniority": "Senior",
    "resume_text": "Experienced Python developer."
}

job = {
    "title": "Senior Python Engineer",
    "company": "Tech Corp",
    "location": "Remote",
    "skills": ["python", "django", "aws"],
    "description": "We need a python expert.",
    "ml_score": 85,
    "ml_features": {"skill_overlap": 2, "location_match": True, "seniority_match": True}
}

print("Running generation...")
try:
    result = explanation_generator.generate_explanation(candidate, job)
    print("[OK] Result:")
    print(ascii(result))
except Exception as e:
    print(f"[X] Generation failed: {e}")
