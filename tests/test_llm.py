"""
Test script for LLM integrations (Groq and Gemini)
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("LLM INTEGRATION TEST")
print("=" * 50)

# Check API keys
groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

print(f"\n1. API Key Check:")
print(f"   GROQ_API_KEY present: {bool(groq_key)}")
print(f"   GEMINI_API_KEY present: {bool(gemini_key)}")

# Test data
candidate = {
    "skills": ["python", "fastapi", "django"],
    "experience_years": 5,
    "preferred_location": "Remote",
    "preferred_seniority": "Senior",
    "resume_text": "Experienced Python developer with 5 years of experience."
}

job = {
    "title": "Senior Python Engineer",
    "company": "Tech Corp",
    "location": "Remote",
    "skills": ["python", "django", "aws"],
    "description": "We need a python expert to build APIs.",
    "ml_score": 85,
    "ml_features": {"skill_overlap": 2, "location_match": True, "seniority_match": True}
}

# Test 1: Groq
print(f"\n2. Testing GROQ (llama3-70b)...")
try:
    from groq import Groq
    groq_client = Groq(api_key=groq_key)
    
    completion = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Reply with a simple JSON: {\"status\": \"ok\"}"},
            {"role": "user", "content": "Test"}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    response = completion.choices[0].message.content
    print(f"   [OK] GROQ works! Response: {response[:100]}")
except Exception as e:
    print(f"   [FAIL] GROQ failed: {e}")

# Test 2: Gemini
print(f"\n3. Testing GEMINI...")
try:
    from core.llm_client import client, GEMINI_MODEL
    from google.genai import types
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents="Reply with a simple JSON: {\"status\": \"ok\"}",
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    print(f"   [OK] GEMINI works! Response: {response.text[:100]}")
except Exception as e:
    print(f"   [FAIL] GEMINI failed: {e}")

# Test 3: Full explanation generation
print(f"\n4. Testing FULL EXPLANATION (uses Groq with Gemini fallback)...")
try:
    from matching.explanations import explanation_generator
    result = explanation_generator.generate_explanation(candidate, job)
    print(f"   [OK] Explanation generated!")
    print(f"   Match Type: {result.get('match_type')}")
    print(f"   Match Score: {result.get('match_score')}")
    print(f"   Reason: {result.get('match_reason', '')[:100]}...")
except Exception as e:
    print(f"   [FAIL] Explanation failed: {e}")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
