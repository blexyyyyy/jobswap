import requests
import sys

BASE_URL = "http://localhost:8000/api"

# 1. Login to get token
login_payload = {"email": "test@example.com", "password": "password123"}
# Note: Ensure this user exists or register first. 
# We'll try to register just in case, ignoring error if exists.
try:
    requests.post(f"{BASE_URL}/auth/register", json={
        "email": "test@example.com", 
        "password": "password123", 
        "name": "Test User"
    })
except:
    pass

login_resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
if login_resp.status_code != 200:
    print(f"❌ Login Failed: {login_resp.text}")
    sys.exit(1)

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login Success")

# 2. Get Feed
feed_resp = requests.get(f"{BASE_URL}/jobs/feed", headers=headers)
if feed_resp.status_code != 200:
    print(f"❌ Feed Failed: {feed_resp.text}")
    sys.exit(1)

jobs = feed_resp.json()
print(f"✅ Feed Fetched. {len(jobs)} jobs found.")

if not jobs:
    print("⚠️ No jobs in feed to test swipe. Skipping swipe test.")
    sys.exit(0)

# 3. Swipe on first job
job_id = jobs[0]["id"]
print(f"Testing swipe on Job ID: {job_id}")

swipe_payload = {"job_id": job_id, "action": "save"}
swipe_resp = requests.post(f"{BASE_URL}/swipe", json=swipe_payload, headers=headers)

if swipe_resp.status_code != 200:
    print(f"❌ Swipe Failed: {swipe_resp.text}")
    sys.exit(1)

print("✅ Swipe 'save' Recorded")

# 4. Verify Saved Jobs
saved_resp = requests.get(f"{BASE_URL}/jobs/saved", headers=headers)
saved_jobs = saved_resp.json().get("jobs", [])
if any(j["id"] == job_id for j in saved_jobs):
    print("✅ Job appears in saved list")
else:
    print(f"❌ Job {job_id} NOT found in saved list. Got: {[j['id'] for j in saved_jobs]}")
    sys.exit(1)
