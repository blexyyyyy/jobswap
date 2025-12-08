import requests
import random
import string

BASE_URL = "http://localhost:8000/api"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def run_test():
    email = f"test_{random_string()}@example.com"
    password = "password123"
    name = "Test User"

    print(f"Testing with {email}...")

    # 1. Register
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "name": name
    })
    
    if resp.status_code != 200:
        print(f"❌ Register Failed: {resp.text}")
        return

    data = resp.json()
    token = data.get("access_token")
    if not token:
        print("❌ No token returned")
        return
    
    print("✅ Register Success")

    # 2. Login (Double check)
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"❌ Login Failed: {resp.text}")
        return
    print("✅ Login Success")

    # 3. Get Profile (Protected Route)
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ Profile Fetch Failed: {resp.text}")
        return
        
    profile = resp.json()
    if profile["email"] == email:
        print("✅ Profile Verified")
    else:
        print(f"❌ Profile Mismatch: {profile}")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Test Crash: {e}")
