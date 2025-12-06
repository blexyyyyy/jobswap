
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_feed():
    # 1. Login
    login_data = {
        "email": "test_v2@example.com",
        "password": "password123"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return

        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get Feed
        print("Fetching feed...")
        resp = requests.get(f"{BASE_URL}/jobs/feed", headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("jobs", [])
            print(f"Feed Success. Got {len(jobs)} jobs.")
            if len(jobs) > 0:
                print(f"First job: {jobs[0]['title']} at {jobs[0]['company']}")
                print(f"Source URL: {jobs[0].get('source_url', 'N/A')}")
        else:
            print(f"Feed Failed: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_feed()
