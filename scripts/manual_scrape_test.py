
import requests
import json

BASE_URL = "http://localhost:8000/api"
LOGIN_DATA = {"email": "test_v2@example.com", "password": "password123"}

def run():
    # 1. Login
    resp = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_DATA)
    if resp.status_code != 200:
        print("Login failed")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Trigger Scrape
    print("Triggering scrape...")
    payload = {"keywords": "Python Developer", "max_jobs": 5}
    scrape_resp = requests.post(f"{BASE_URL}/jobs/scrape", json=payload, headers=headers)
    
    if scrape_resp.status_code == 200:
        data = scrape_resp.json()
        print(json.dumps(data, indent=2))
        if "Remotive" in str(data.get("sources", [])):
            print("\nSUCCESS: Remotive source found!")
        else:
            print("\nWARNING: Remotive source NOT found (maybe rate limited?)")
    else:
        print(f"Scrape failed: {scrape_resp.text}")

if __name__ == "__main__":
    run()
