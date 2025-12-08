import requests
import sqlite3
import time
import os

BASE_URL = "http://localhost:8000/api"
DB_PATH = "jobswipe.db"

# 1. Login
print("🔑 Logging in...")
requests.post(f"{BASE_URL}/auth/register", json={"email": "apply_tester@example.com", "password": "pass", "name": "Apply Tester"})
token = requests.post(f"{BASE_URL}/auth/login", json={"email": "apply_tester@example.com", "password": "pass"}).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Token acquired")

# 2. Upload Dummy Resume
print("📄 Uploading Resume...")
with open("dummy_resume.txt", "w") as f:
    f.write("I am a software engineer with 5 years of experience in Python.")

with open("dummy_resume.txt", "rb") as f:
    files = {"file": ("dummy_resume.txt", f, "text/plain")}
    # Note: Using /api/resume/upload
    resp = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files=files) 

if resp.status_code != 200:
    print(f"❌ Upload Failed: {resp.text}")
    with open("trace.txt", "w") as f:
        f.write(resp.text)
else:
    print(f"✅ Resume Uploaded: {resp.json().get('file_saved')}")

# 3. Create a Dummy Job
print("🏢 inserting dummy job...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("INSERT INTO jobs (title, company, description, source_url) VALUES ('Target Job', 'Target Co', 'Desc', 'manual')")
job_id = cursor.lastrowid
conn.commit()
conn.close()
print(f"✅ Created Job ID: {job_id}")

# 4. Trigger Auto-Apply
print("🚀 Triggering Auto-Apply...")
payload = {
    "job_ids": [job_id],
    "override_email": "recruiter@target.com"
}
resp = requests.post(f"{BASE_URL}/apply", json=payload, headers=headers)
if resp.status_code != 200:
    print(f"❌ Apply Call Failed: {resp.text}")
else:
    data = resp.json()
    print(f"✅ Applied! Queued: {data['queued']}, Failed: {data['failed']}")

# 5. Check DB Status
print("🔍 Checking Queue Status...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
time.sleep(2) # Give background task a moment
cursor.execute("SELECT status, to_email FROM auto_apply_queue WHERE job_id = ? AND user_id = (SELECT id FROM users WHERE email='apply_tester@example.com')", (job_id,))
row = cursor.fetchone()
if row:
    print(f"✅ Queue Row Found: Status = {row[0]}, To = {row[1]}")
    if row[0] == 'sent':
        print("🎉 SUCCESS: Validated 'sent' status (Mock Email)")
    else:
        print(f"⚠️ Status is {row[0]}. (Might be pending if background worker is slow/failed)")
else:
    print("❌ No queue row found!")

conn.close()

# Cleanup
try:
    os.remove("dummy_resume.txt")
except:
    pass
