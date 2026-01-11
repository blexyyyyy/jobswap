
import sys
import os
import asyncio
import json

sys.path.append(os.getcwd())

from matching.explanations import explanation_generator
import app.core.config as config
import os

# Check for API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Sample Data mimicking a real scenario
SAMPLE_USER = {
    "skills": ["python", "fastapi", "react", "sql"],
    "experience_years": 3,
    "preferred_location": "Remote",
    "preferred_seniority": "Mid-Level",
    "resume_text": "Full stack developer with experience in building scalable web apps using Python and React."
}

SAMPLE_JOB = {
    "title": "Senior Python Engineer",
    "company": "TechCorp",
    "location": "Remote",
    "skills": ["python", "django", "aws", "postgresql"],
    "description": "We are looking for a senior engineer to lead our backend team. Must have strong Python skills.",
    "ml_score": 85,
    "ml_features": {"skill_overlap": 2, "location_match": 1.0, "seniority_match": 0.0}
}

async def test_explanation():
    print("--- Debugging Explanation Generation ---")
    print(f"API Key Present: {bool(GEMINI_API_KEY)}")
    
    print("\n[Input Data]")
    print(f"User: {SAMPLE_USER}")
    print(f"Job: {SAMPLE_JOB}\n")

    try:
        # Call the generator directly
        result = explanation_generator.generate_explanation(SAMPLE_USER, SAMPLE_JOB)
        
        print("\n[Generated Result]")
        print(json.dumps(result, indent=2))
        
        # Check quality indicators
        if result.get("match_reason") == "Good potential match based on your profile.":
            print("\n[WARNING] This looks like the FALLBACK response! The LLM call likely failed or parsing failed.")
        elif result.get("match_reason") == "This job aligns with your skills and experience level.":
            print("\n[WARNING] This looks like the Exception FALLBACK response!")
        else:
            print("\n[SUCCESS] Response appears to be from LLM.")

    except Exception as e:
        print(f"\n[ERROR] execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # The generator is synchronous, but let's wrap it if needed or just call it
    # generate_explanation is sync in the code I viewed earlier
    test_explanation()
