import requests
import sys
import time

BASE_URL = "http://localhost:8000/api"

# 1. Login to get token
try:
    requests.post(f"{BASE_URL}/auth/register", json={
        "email": "scrape_tester@example.com", 
        "password": "password123", 
        "name": "Scrape Tester"
    })
except:
    pass

login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "scrape_tester@example.com", "password": "password123"})
if login_resp.status_code != 200:
    print(f"❌ Login Failed: {login_resp.text}")
    sys.exit(1)

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login Success")

# 2. Trigger Scrape
print("Triggering Scrape (this may take 10-20 seconds)...")
scrape_payload = {"keywords": "python developer", "max_jobs": 10}
start = time.time()
scrape_resp = requests.post(f"{BASE_URL}/jobs/scrape/", json=scrape_payload, headers=headers)
duration = time.time() - start

if scrape_resp.status_code != 200:
    print(f"❌ Scrape Failed: {scrape_resp.text}")
    sys.exit(1)

print(f"✅ Scrape Completed in {duration:.2f}s")
print(f"Response: {scrape_resp.json()}")

# 3. Check Feed
print("Fetching Feed...")
feed_resp = requests.get(f"{BASE_URL}/jobs/feed", headers=headers)
if feed_resp.status_code != 200:
    print(f"❌ Feed Fetched Failed: {feed_resp.text}")
    sys.exit(1)

jobs = feed_resp.json()["jobs"]
print(f"✅ Feed Fetched. {len(jobs)} jobs in feed.")

# Check for scraped jobs
new_jobs = [j for j in jobs if j.get("source_url") and ("remoteok" in j.get("source_url") or "remotive" in j.get("source_url") or "timesjobs" in j.get("source_url"))]
if new_jobs:
    print(f"✅ Found {len(new_jobs)} newly scraped jobs in feed!")
    print(f"Sample: {new_jobs[0]['title']} at {new_jobs[0]['company']}")
else:
    print("⚠️ No obvious new jobs found. Check db?")
