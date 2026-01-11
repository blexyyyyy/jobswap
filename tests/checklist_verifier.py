import os
import sys
from dotenv import load_dotenv
import requests

print("--- DIAGNOSTIC CHECKLIST REPORT ---\n")

# 1. Reload Env
load_dotenv(override=True)
key = os.getenv("GROQ_API_KEY")

# Check: Key Loaded
if key:
    print(f"[PASS] Key Loaded: Yes")
else:
    print(f"[FAIL] Key Loaded: No")
    sys.exit(1)

# Check: Format (Quotes/Spaces)
repr_key = repr(key)
if key.strip() != key:
    print(f"[FAIL] .env Format: Key has whitespace! -> {repr_key}")
elif "'" in key or '"' in key:
    # Heuristic: keys usually don't have quotes inside them unless mistakenly added
    # But some keys might. Let's warn.
    print(f"[WARN] .env Format: Key contains quotes? -> {repr_key}")
else:
    print(f"[PASS] .env Format: Clean (No extra whitespace/quotes detected) -> {repr_key}")

# Check: Header Format
# We simulate what the SDK does
header_val = f"Bearer {key}"
expected_prefix = "Bearer gsk_"
if header_val.startswith(expected_prefix):
    print(f"[PASS] Header Format: Correctly formed 'Bearer gsk_...'")
else:
    print(f"[FAIL] Header Format: Malformed or key missing 'gsk_' prefix -> '{header_val[:15]}...'")

# Check: Active API Call (Connectivity + Validity)
print("\n--- Testing API Connectivity & Validity ---")
try:
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": header_val,
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        },
        timeout=10
    )
    
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("[PASS] API Key: Valid and Working!")
        print(f"Response: {resp.json()}")
    elif resp.status_code == 401:
        print("[FAIL] API Key: Rejected (401 Unauthorized).")
        print("       Run curl/requests yourself to verify. The key is definitely invalid.")
        print(f"       Body: {resp.text}")
    else:
        print(f"[WARN] API Error: {resp.status_code}")
        print(f"       Body: {resp.text}")

except Exception as e:
    print(f"[FAIL] Network Connection: {e}")

print("\n--- End of Report ---")
