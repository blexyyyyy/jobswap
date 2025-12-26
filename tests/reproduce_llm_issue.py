
import sys
import os
import asyncio
from typing import Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from app.llm.wrapper import LLMWrapper
from matching.explanations import explanation_generator

async def test_generation():
    print("--- Testing LLMWrapper ---")
    wrapper = LLMWrapper(provider_names=["gemini"]) # Force Gemini
    try:
        res = wrapper.generate("Say hello", temperature=0.7)
        print(f"Wrapper Result: {res}")
        if not res.get("text"):
            print("ERROR: Wrapper returned empty text!")
    except Exception as e:
        print(f"Wrapper Error: {e}")

    print("\n--- Testing Explanation Generator ---")
    candidate = {
        "skills": ["python", "fastapi"], 
        "experience_years": 5, 
        "preferred_location": "Remote",
        "preferred_seniority": "Senior",
        "resume_text": "Experienced Python developer."
    }
    job = {
        "title": "Senior Backend Engineer",
        "company": "Tech Corp",
        "location": "Remote",
        "skills": ["python", "aws", "docker"],
        "description": "We need a python expert.",
        "ml_score": 95,
        "ml_features": {"skill_overlap": 1}
    }
    
    explanation = explanation_generator.generate_explanation(candidate, job)
    print(f"Explanation Result: {explanation}")
    
    if "match_reason" not in explanation:
        print("ERROR: Missing 'match_reason' key!")

if __name__ == "__main__":
    asyncio.run(test_generation())
