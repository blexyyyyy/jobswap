"""
FastAPI Backend for JobSwipe
Handles user authentication and job matching API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sqlite3
import shutil
import os


from app.core.config import DB_PATH
from app.core.config import DB_PATH
from app.api.routes import auth, jobs, chat, swipe, scrape, profile, resume, apply, ml
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    init_database()
    yield
    # Shutdown events if any


# Initialize FastAPI app
app = FastAPI(
    title="JobSwipe API",
    description="AI-powered job matching API",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_detail = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    print(f"Global Error: {error_detail}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc), "trace": error_detail}
    )

@app.get("/")
async def root():
    return {"message": "JobSwipe API is operational. If you see this, the frontend is not being served correctly by Vercel."}

@app.get("/api/debug/db-check")
async def debug_db():
    import os
    import sqlite3
    
    db_status = {
        "db_path": DB_PATH,
        "exists": os.path.exists(DB_PATH),
        "size": os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0,
        "src_exists": os.path.exists("jobswipe.db"),
        "tables": [],
        "job_count": 0,
        "user_count": 0
    }
    
    if db_status["exists"]:
        try:
            conn = sqlite3.connect(DB_PATH)
            # List tables
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            db_status["tables"] = [t[0] for t in tables]
            
            # Count jobs
            if "jobs" in db_status["tables"]:
                db_status["job_count"] = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
                
            # Count users
            if "users" in db_status["tables"]:
                db_status["user_count"] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                
            conn.close()
        except Exception as e:
            db_status["error"] = str(e)
            
    return db_status

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
    if os.getenv("VERCEL"):
        # Copy existing DB to /tmp if it doesn't exist
        if not os.path.exists(DB_PATH):
            try:
                # Source is in the project root
                src = "jobswipe.db"
                if os.path.exists(src):
                    print(f"Copying {src} to {DB_PATH} for Vercel execution...")
                    shutil.copy2(src, DB_PATH)
                else:
                    print(f"Warning: Source database {src} not found!")
            except Exception as e:
                print(f"Error copying database: {e}")
    # Local development init
    conn = sqlite3.connect(DB_PATH)
    try:
        if os.path.exists("database/schema.sql"):
            with open("database/schema.sql", "r") as f:
                conn.executescript(f.read())
            conn.commit()
    except Exception as e:
        print(f"Database init error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    # init_database calls are now handled by lifespan
    uvicorn.run(app, host="0.0.0.0", port=8000)
