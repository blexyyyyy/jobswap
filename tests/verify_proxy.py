import requests
import sys

# Target Vite Server
BASE_URL = "http://localhost:3000/api"

print("🔍 Testing Vite Proxy at http://localhost:3000/api ...")

# 1. Login (Hit Backend directly to get valid token first, or try proxy if auth route is proxied)
# Let's try hitting backend directly for token to isolate proxy test for /feed
AUTH_URL = "http://localhost:8000/api"
try:
    login_resp = requests.post(f"{AUTH_URL}/auth/login", json={"email": "test@example.com", "password": "password123"})
    if login_resp.status_code != 200:
        print(f"❌ Backend Login Failed: {login_resp.text}")
        sys.exit(1)
    token = login_resp.json()["access_token"]
    print("✅ Got Backend Token")
except Exception as e:
    print(f"❌ Backend Connection Failed: {e}")
    sys.exit(1)

# 2. Access Feed via Proxy
headers = {"Authorization": f"Bearer {token}"}
try:
    feed_resp = requests.get(f"{BASE_URL}/jobs/feed", headers=headers, timeout=10)
    print(f"Proxy Response Code: {feed_resp.status_code}")
    if feed_resp.status_code == 200:
        print("✅ Proxy Works! Got Feed.")
    else:
        print(f"❌ Proxy Failed: {feed_resp.status_code} - {feed_resp.text[:200]}")
except Exception as e:
    print(f"❌ Proxy Connection Error: {e}")
