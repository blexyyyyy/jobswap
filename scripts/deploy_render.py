"""
Deploy JobSwipe backend to Render using their API
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Render API configuration
RENDER_API_KEY = "rnd_FONPdB9EsrRFFqq5oYzvhXEg65zQ"
RENDER_API_URL = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

# Get API keys from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
JWT_SECRET = "TZ8bJ-sD11IU3gHnfYCC4LMofjbf2qcwPUUm7sq2m3Y"

print("=== Deploying JobSwipe Backend to Render ===\n")

# Step 1: Create PostgreSQL database
print("1. Creating PostgreSQL database...")
db_payload = {
    "type": "pgsql",
    "name": "jobswipe-db",
    "databaseName": "jobswipe",
    "databaseUser": "jobswipe",
    "plan": "free",
    "region": "oregon"
}

try:
    db_response = requests.post(
        f"{RENDER_API_URL}/postgres",
        headers=headers,
        json=db_payload
    )
    
    if db_response.status_code in [200, 201]:
        db_data = db_response.json()
        print(f"   ✓ Database created: {db_data.get('name')}")
        database_id = db_data.get('id')
        # Get internal connection string
        internal_db_url = db_data.get('internalConnectionString', '')
        print(f"   Database ID: {database_id}")
    else:
        print(f"   ✗ Database creation failed: {db_response.status_code}")
        print(f"   Response: {db_response.text}")
        # Try to continue anyway - database might already exist
        database_id = None
        internal_db_url = ""
except Exception as e:
    print(f"   ✗ Error creating database: {e}")
    database_id = None
    internal_db_url = ""

# Step 2: Create Web Service
print("\n2. Creating web service...")
service_payload = {
    "type": "web_service",
    "name": "jobswipe-backend",
    "repo": "https://github.com/blexyyyyy/jobswap",
    "branch": "main",
    "runtime": "python",
    "buildCommand": "pip install -r requirements.txt",
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "plan": "free",
    "region": "oregon",
    "envVars": [
        {"key": "PYTHON_VERSION", "value": "3.11.0"},
        {"key": "GROQ_API_KEY", "value": GROQ_API_KEY},
        {"key": "GEMINI_API_KEY", "value": GEMINI_API_KEY},
        {"key": "JWT_SECRET", "value": JWT_SECRET},
        {"key": "CORS_ORIGINS", "value": "https://frontend-etw8ni0aw-veerats-projects-9d2ad569.vercel.app"},
    ]
}

# Add database URL if we have it
if internal_db_url:
    service_payload["envVars"].append({"key": "DATABASE_URL", "value": internal_db_url})

try:
    service_response = requests.post(
        f"{RENDER_API_URL}/services",
        headers=headers,
        json=service_payload
    )
    
    if service_response.status_code in [200, 201]:
        service_data = service_response.json()
        print(f"   ✓ Service created: {service_data.get('name')}")
        service_url = service_data.get('serviceDetails', {}).get('url', 'N/A')
        print(f"   Service URL: {service_url}")
        print(f"\n✓ Deployment initiated!")
        print(f"\nBackend URL: https://{service_url}")
        print(f"API Docs: https://{service_url}/docs")
    else:
        print(f"   ✗ Service creation failed: {service_response.status_code}")
        print(f"   Response: {service_response.text}")
except Exception as e:
    print(f"   ✗ Error creating service: {e}")

print("\n=== Deployment Complete ===")
print("\nNext steps:")
print("1. Wait for Render to build and deploy (5-10 minutes)")
print("2. Check deployment status at: https://dashboard.render.com")
print("3. Run database initialization: python init_db.py")
print("4. Update Vercel frontend with backend URL")
