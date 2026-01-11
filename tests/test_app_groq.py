"""
End-to-end test for Groq integration in JobSwipe
Tests the explanation generation through the actual app flow
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

print("=== JobSwipe Groq Integration Test ===\n")

# Step 1: Login
print("1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "debuguser@example.com", "password": "password"}
)

if login_response.status_code != 200:
    print(f"   [FAIL] Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"   [PASS] Logged in successfully")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Get job feed
print("\n2. Fetching job feed...")
jobs_response = requests.get(f"{BASE_URL}/jobs/feed", headers=headers)

if jobs_response.status_code != 200:
    print(f"   [FAIL] Failed to fetch jobs: {jobs_response.status_code}")
    exit(1)

jobs_data = jobs_response.json()
# Handle both list and dict responses
if isinstance(jobs_data, dict):
    jobs = jobs_data.get("jobs", [])
else:
    jobs = jobs_data

if not jobs:
    print("   [WARN] No jobs in feed")
    print(f"   Response: {jobs_data}")
    exit(0)

print(f"   [PASS] Fetched {len(jobs)} jobs")

# Step 3: Test explanation generation for first job
first_job = jobs[0]
job_id = first_job["id"]
print(f"\n3. Testing explanation generation for job #{job_id}: '{first_job['title']}'")

explanation_response = requests.get(
    f"{BASE_URL}/jobs/{job_id}/explanation",
    headers=headers
)

if explanation_response.status_code != 200:
    print(f"   [FAIL] Explanation request failed: {explanation_response.status_code}")
    print(f"   Response: {explanation_response.text}")
    exit(1)

explanation = explanation_response.json()
print(f"   [PASS] Explanation generated successfully!")

# Step 4: Verify explanation structure and source
print("\n4. Verifying explanation content...")
required_fields = ["match_reason", "match_score", "missing_skills", "career_tip", "match_type", "generator_source"]
missing_fields = [f for f in required_fields if f not in explanation]

if missing_fields:
    print(f"   [FAIL] Missing fields: {missing_fields}")
    exit(1)

print(f"   [PASS] All required fields present")

# Step 5: Check generator source
generator_source = explanation.get("generator_source", "unknown")
print(f"\n5. Generator Source: {generator_source}")

if generator_source == "groq":
    print("   [SUCCESS] ✓ Using Groq API!")
elif generator_source == "gemini":
    print("   [INFO] Using Gemini fallback")
elif generator_source == "fallback_static":
    print("   [WARN] Using static fallback (both APIs failed)")
else:
    print(f"   [UNKNOWN] Unexpected source: {generator_source}")

# Step 6: Display explanation
print("\n6. Generated Explanation:")
print(f"   Match Type: {explanation['match_type']}")
print(f"   Match Score: {explanation['match_score']}%")
print(f"   Reason: {explanation['match_reason'][:100]}...")
print(f"   Missing Skills: {', '.join(explanation['missing_skills']) if explanation['missing_skills'] else 'None'}")
print(f"   Career Tip: {explanation['career_tip']}")

print("\n=== Test Complete ===")
if generator_source == "groq":
    print("✓ Groq integration is WORKING!")
else:
    print(f"⚠ Using fallback: {generator_source}")
