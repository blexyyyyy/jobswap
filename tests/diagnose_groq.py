import os
import requests
from dotenv import load_dotenv
from groq import Groq

# Load environment
load_dotenv()
raw_key = os.getenv("GROQ_API_KEY")

print("--- 1. Invisible Character Check ---")
print(f"Raw Key from .env: {repr(raw_key)}")
if raw_key:
    stripped_key = raw_key.strip()
    print(f"Stripped Key:      {repr(stripped_key)}")
else:
    stripped_key = None
    print("Key is None!")

print("\n--- 2. Request Header Inspection (Python requests) ---")
if stripped_key:
    try:
        req = requests.Request(
            "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {stripped_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1}
        )
        prepped = req.prepare()
        # Mask key in output for safety, but check length
        auth_header = prepped.headers.get('Authorization', '')
        print(f"Authorization Header Sent: {auth_header[:15]}... (Length: {len(auth_header)})")
        
        s = requests.Session()
        r = s.send(prepped)
        print("Status:", r.status_code)
        print("Response Body:", r.text[:200]) # First 200 chars
    except Exception as e:
        print(f"Request failed: {e}")

print("\n--- 3. SDK Verification (with stripped key) ---")
if stripped_key:
    try:
        client = Groq(api_key=stripped_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":"ping"}],
            max_tokens=1
        )
        print("SDK Success! Response:", resp.choices[0].message.content)
    except Exception as e:
        print("SDK Failed:", e)
