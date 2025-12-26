import requests
import json
import time

def test_login(port, label):
    print(f"\n--- Testing {label} (Port {port}) ---")
    url = f"http://localhost:{port}/api/auth/login"
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        print(f"Sending POST to {url}...")
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status Code: {response.status_code}")
        # print("Response Headers:", response.headers)
        
        try:
            content = response.content.decode('utf-8')
            if not content:
                print("❌ Response body is EMPTY!")
            else:
                try:
                    json_resp = response.json()
                    print("✅ JSON Response received (Success/Failure handled by app code)")
                    # print("JSON:", json.dumps(json_resp, indent=2))
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to decode JSON: {e}")
                    print(f"Raw content preview: {content[:100]}...")
        except Exception as e:
            print(f"Error reading content: {e}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Refused on port {port} (Service might be down)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_login(8000, "Direct Backend")
    test_login(3000, "Vite Proxy")
