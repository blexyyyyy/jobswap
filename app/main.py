"""
FastAPI Backend for JobSwipe
Handles user authentication and job matching API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sqlite3
import os

from app.core.config import DB_PATH
from app.api.routes import auth, jobs, chat, swipe, scrape, profile, resume, apply, ml

# Initialize FastAPI app
app = FastAPI(
    title="JobSwipe API",
    description="AI-powered job matching API",
    version="1.0.0"
)

# CORS middleware for frontend
# Get allowed origins from environment variable or use wildcard for development
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(profile.router, prefix="/api/auth/profile", tags=["Profile"]) # Note: URL path adjustment
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(swipe.router, prefix="/api/swipe", tags=["Swipe"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(scrape.router, prefix="/api/jobs/scrape", tags=["Scrape"])
app.include_router(apply.router, prefix="/api/apply", tags=["Apply"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML"])


# ========== Health Check ==========

@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ========== Initialize Database ==========

def init_database():
    """Initialize database with schema."""
    conn = sqlite3.connect(DB_PATH)
    try:
        with open("database/schema.sql", "r") as f:
            conn.executescript(f.read())
        conn.commit()
    except Exception as e:
        print(f"Database init error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    init_database()
    uvicorn.run(app, host="0.0.0.0", port=8000)
