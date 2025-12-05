#!/usr/bin/env python3
"""Diagnostic script for Gemini API issues."""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

print(f"✅ API Key loaded: {API_KEY[:20]}...")

# Initialize client
client = genai.Client(api_key=API_KEY)
print("✅ Client initialized")

# Test 1: List available models
print("\n--- Test 1: List Models ---")
try:
    models = client.models.list()
    print("✅ Successfully listed models")
    for model in models:
        if "gemini" in model.name.lower():
            print(f"  - {model.name}: {model.display_name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print(f"   Error type: {type(e).__name__}")

# Test 2: Simple text generation
print("\n--- Test 2: Simple Text Generation ---")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say 'Hello World' and nothing else."
    )
    print(f"✅ Text generation successful")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Error in text generation: {e}")
    print(f"   Error type: {type(e).__name__}")

# Test 3: JSON-only generation (the issue likely here)
print("\n--- Test 3: JSON Generation ---")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents='Return only this JSON: {"test": "value"}',
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )
    print(f"✅ JSON generation successful")
    print(f"   Response: {response.text}")
    data = json.loads(response.text)
    print(f"   Parsed: {data}")
except Exception as e:
    print(f"❌ Error in JSON generation: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error code: {getattr(e, 'code', 'N/A')}")
    print(f"   Status code: {getattr(e, 'status_code', 'N/A')}")
    if hasattr(e, 'details'):
        print(f"   Details: {e.details}")

# Test 4: Embeddings (if 404 is about embeddings)
print("\n--- Test 4: Embeddings ---")
try:
    result = client.models.embed_content(
        model="text-embedding-004",
        contents="test text"
    )
    print(f"✅ Embeddings successful")
    if result.embeddings:
        print(f"   Embedding dimensions: {len(result.embeddings[0].values)}")
except Exception as e:
    print(f"❌ Error in embeddings: {e}")
    print(f"   Error type: {type(e).__name__}")

print("\n=== Diagnostic Complete ===")
print("\n=== Diagnostic Complete ===")
