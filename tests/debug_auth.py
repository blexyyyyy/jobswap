import requests

BASE_URL = "http://localhost:8000/api"

print("🔍 Testing Register...")
try:
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "debug_auth_new@example.com", 
        "password": "password123", 
        "name": "Debug User"
    })
    print(f"Status: {resp.status_code}")
    print(f"Text: {resp.text[:500]}") # Print first 500 chars
except Exception as e:
    print(f"Connection Error: {e}")

print("\n🔍 Testing Login...")
try:
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "debug_auth_new@example.com", 
        "password": "password123"
    })
    print(f"Status: {resp.status_code}")
    print(f"Text: {resp.text[:500]}")
except Exception as e:
    print(f"Connection Error: {e}")
