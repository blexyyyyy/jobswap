"""
FastAPI Backend for JobSwipe
Handles user authentication and job matching API
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import sqlite3
import jwt

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="JobSwipe API",
    description="AI-powered job matching API",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
# Use a consistent key for development so reloads don't invalidate tokens
SECRET_KEY = os.getenv("JWT_SECRET", "development-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
DB_PATH = "database/jobmatcher.db"

security = HTTPBearer()


# ========== Pydantic Models ==========

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    preferred_location: Optional[str] = None
    preferred_seniority: Optional[str] = None
    resume_text: Optional[str] = None


class SwipeAction(BaseModel):
    job_id: int
    action: str  # 'apply', 'skip', 'save'


class ChatMessage(BaseModel):
    message: str


class JobScrapeRequest(BaseModel):
    keywords: str
    location: Optional[str] = "India"
    max_jobs: Optional[int] = 10


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ========== Database Helpers ==========

from database.connection import get_db_connection

def get_db():
    """Get database connection (Dependency).
    
    NOTE: This is a legacy helper for "Depends(get_db)" usage if we were yielding.
    But since we switched to context managers inside endpoints for safety,
    we can deprecate this or make it yield using the manager.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash


def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (int(payload["sub"]),))
        user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return dict(user)


# ========== Auth Endpoints ==========

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        password_hash = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (user.email, password_hash, user.name)
        )
        conn.commit()
        user_id = cursor.lastrowid
    
    # Generate token
    token = create_access_token(user_id, user.email)
    
    return TokenResponse(
        access_token=token,
        user={"id": user_id, "email": user.email, "name": user.name}
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """Login and get access token."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
        db_user = cursor.fetchone()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate token
    token = create_access_token(db_user["id"], db_user["email"])
    
    return TokenResponse(
        access_token=token,
        user={
            "id": db_user["id"],
            "email": db_user["email"],
            "name": db_user["name"]
        }
    )


@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "phone": current_user["phone"],
        "skills": current_user["skills"],
        "experience_years": current_user["experience_years"],
        "preferred_location": current_user["preferred_location"],
        "preferred_seniority": current_user["preferred_seniority"],
    }


@app.put("/api/auth/profile")
async def update_profile(profile: UserProfile, current_user: dict = Depends(get_current_user)):
    """Update user profile."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET
                name = COALESCE(?, name),
                phone = COALESCE(?, phone),
                skills = COALESCE(?, skills),
                experience_years = COALESCE(?, experience_years),
                preferred_location = COALESCE(?, preferred_location),
                preferred_seniority = COALESCE(?, preferred_seniority),
                resume_text = COALESCE(?, resume_text),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            profile.name,
            profile.phone,
            profile.skills,
            profile.experience_years,
            profile.preferred_location,
            profile.preferred_seniority,
            profile.resume_text,
            current_user["id"]
        ))
        conn.commit()
    
    return {"message": "Profile updated successfully"}


# ========== Jobs Endpoints ==========

@app.get("/api/jobs/feed")
async def get_job_feed(current_user: dict = Depends(get_current_user)):
    """Get job feed for the current user (excluding already swiped jobs)."""
    try:
        all_jobs = []
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get jobs not yet swiped by user
            cursor.execute("""
                SELECT j.* FROM jobs j
                WHERE j.id NOT IN (
                    SELECT job_id FROM user_swipes WHERE user_id = ?
                )
                ORDER BY j.created_at DESC
            """, (current_user["id"],))
            
            all_jobs = [dict(row) for row in cursor.fetchall()]
        
        # Format jobs and calculate initial sort score
        from matching.explanations import explanation_generator
        
        user_profile = {
            "skills": current_user["skills"].split(",") if current_user["skills"] else [],
            "experience_years": current_user["experience_years"],
            "preferred_location": current_user["preferred_location"],
            "preferred_seniority": current_user["preferred_seniority"],
            "resume_text": current_user["resume_text"]
        }
        
        user_skills_set = set(s.strip().lower() for s in user_profile["skills"])

        processed_jobs = []
        for job in all_jobs:
            # Convert skills from string to array
            if job.get("skills"):
                job["skills"] = [s.strip() for s in job["skills"].split(",")]
            else:
                job["skills"] = []
                
            # Initial Scoring (for sorting)
            job_skills_set = set(s.lower() for s in job["skills"])
            overlap = len(user_skills_set & job_skills_set)
            
            # Simple heuristic score: overlap * 10, capped at 90 base
            # If title matches "Senior" and user is "Senior", bonus
            score = 50 + (overlap * 10)
            
            # Title match bonus
            if user_profile["preferred_seniority"] and user_profile["preferred_seniority"].lower() in job["title"].lower():
                score += 10
            
            job["match_score"] = min(95, score)
            job["logo_emoji"] = ["🚀", "💡", "📊", "🤖", "☁️", "🌱", "🏗️", "💰"][job["id"] % 8]
            processed_jobs.append(job)

        # Sort by heuristic score DESC
        processed_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Take all jobs (user asked for all 74)
        jobs = processed_jobs
            
        # === Parallel Explanation Generation ===
        import asyncio
        from matching.explanations import explanation_generator
        
        async def fetch_explanation(job):
            try:
                # Clean description
                raw_desc = job.get("description", "") or ""
                try:
                    from bs4 import BeautifulSoup
                    import re
                    soup = BeautifulSoup(raw_desc, "html.parser")
                    clean_desc = soup.get_text(separator=" ")
                    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
                    job["description"] = clean_desc[:500] 
                except Exception:
                    job["description"] = raw_desc[:500]

                job_summary = {
                    "title": job["title"],
                    "company": job["company"],
                    "location": job["location"],
                    "skills": job["skills"],
                    "description": job["description"]
                }
                
                # Run sync LLM call in thread pool to avoid blocking event loop
                explanation = await asyncio.to_thread(explanation_generator.generate_explanation, user_profile, job_summary)
                
                job["match_explanation"] = explanation
                if explanation.get("match_score"):
                    job["match_score"] = explanation["match_score"]
            except Exception as e:
                # print(f"Error generating explanation for job {job['id']}: {e}")
                # Fallback
                common_count = len(set(job["skills"]) & set(user_profile["skills"]))
                job["match_explanation"] = {
                    "match_reason": f"Matches {common_count} of your skills.",
                    "match_type": "neutral",
                    "match_score": 50 + (common_count * 10),
                    "missing_skills": [],
                    "career_tip": "Review requirements."
                }

        # Run all explanation tasks concurrently
        # Limit concurrency to avoid hitting rate limits too hard if we had many jobs, 
        # but for 20 jobs it should be fine.
        if jobs:
            await asyncio.gather(*[fetch_explanation(job) for job in jobs])
        
        return {"jobs": jobs}
    except Exception as e:
        import traceback
        with open("server_error.log", "a") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/swipe")
async def record_swipe(swipe: SwipeAction, current_user: dict = Depends(get_current_user)):
    """Record a user's swipe action on a job."""
    if swipe.action not in ("apply", "skip", "save"):
        raise HTTPException(status_code=400, detail="Invalid action")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_swipes (user_id, job_id, action) VALUES (?, ?, ?)",
                (current_user["id"], swipe.job_id, swipe.action)
            )
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": f"Recorded {swipe.action} for job {swipe.job_id}"}


# ========== Resume Upload ==========

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload and parse a resume."""
    from utils.file_handler import extract_text_from_file
    from parsers.resume_parser import resume_parser
    
    # Extract text
    try:
        text = await extract_text_from_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File processing error: {str(e)}")
    
    # Parse with LLM
    try:
        parsed_data = resume_parser.parse_resume(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
        
    # Update user profile
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        skills_str = ",".join(parsed_data.get("skills", []))
        
        cursor.execute("""
            UPDATE users SET
                name = COALESCE(?, name),
                email = COALESCE(?, email),
                phone = COALESCE(?, phone),
                skills = ?,
                experience_years = ?,
                resume_text = ?,
                preferred_location = COALESCE(?, preferred_location),
                preferred_seniority = COALESCE(?, preferred_seniority),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            parsed_data.get("name"),
            parsed_data.get("email"),
            parsed_data.get("phone"),
            skills_str,
            parsed_data.get("experience_years"),
            text, # Store raw text too? Or summary? storing raw text as resume_text
            parsed_data.get("preferred_location"),
            parsed_data.get("preferred_seniority"),
            current_user["id"]
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    conn.close()
    
    return {
        "message": "Resume uploaded and parsed successfully",
        "parsed_data": parsed_data
    }


@app.get("/api/jobs/saved")
async def get_saved_jobs(current_user: dict = Depends(get_current_user)):
    """Get user's saved jobs."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT j.* FROM jobs j
        JOIN user_swipes us ON j.id = us.job_id
        WHERE us.user_id = ? AND us.action = 'save'
        ORDER BY us.created_at DESC
    """, (current_user["id"],))
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"jobs": jobs}


@app.get("/api/jobs/applied")
async def get_applied_jobs(current_user: dict = Depends(get_current_user)):
    """Get user's applied jobs."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT j.* FROM jobs j
        JOIN user_swipes us ON j.id = us.job_id
        WHERE us.user_id = ? AND us.action = 'apply'
        ORDER BY us.created_at DESC
    """, (current_user["id"],))
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"jobs": jobs}


# ========== Chat Endpoints ==========

@app.get("/api/chat/{job_id}")
async def get_chat_messages(job_id: int, current_user: dict = Depends(get_current_user)):
    """Get all chat messages for a job application."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM messages
        WHERE user_id = ? AND job_id = ?
        ORDER BY created_at ASC
    """, (current_user["id"], job_id))
    
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"messages": messages}


@app.post("/api/chat/{job_id}")
async def send_message(job_id: int, msg: ChatMessage, current_user: dict = Depends(get_current_user)):
    """Send a message to employer."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Insert user message
    cursor.execute("""
        INSERT INTO messages (user_id, job_id, sender_type, message)
        VALUES (?, ?, 'user', ?)
    """, (current_user["id"], job_id, msg.message))
    conn.commit()
    
    # Generate AI employer response (demo mode)
    import random
    responses = [
        "Thanks for reaching out! We've reviewed your application and would like to schedule an interview. Are you available this week?",
        "Hello! Your profile looks great. Could you tell us more about your experience with {skill}?",
        "Hi there! We're excited about your application. What's your expected salary range?",
        "Thank you for applying! We'd love to learn more about your recent projects. Can you share some details?",
        "Great to hear from you! When would be a good time for a quick call to discuss this role?"
    ]
    
    employer_response = random.choice(responses)
    
    # Get job info to personalize response
    cursor.execute("SELECT skills FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    if job and job["skills"]:
        skills = job["skills"].split(",")
        employer_response = employer_response.replace("{skill}", skills[0].strip())
    
    # Insert employer response
    cursor.execute("""
        INSERT INTO messages (user_id, job_id, sender_type, message)
        VALUES (?, ?, 'employer', ?)
    """, (current_user["id"], job_id, employer_response))
    conn.commit()
    conn.close()
    
    return {"message": "Message sent", "employer_response": employer_response}


# ========== Job Scraping Endpoint ==========

@app.post("/api/jobs/scrape")
async def scrape_jobs(request: JobScrapeRequest, current_user: dict = Depends(get_current_user)):
    """Scrape jobs from multiple sources (Remotive, RemoteOK, etc.) and add to database."""
    try:
        from scrapers.unified_scraper import fetch_all_jobs
        from database.db_manager import insert_job
        
        # Scrape jobs
        # Sources: Remotive, RemoteOK, Arbeitnow, WeWorkRemotely, Jobicy
        # Limit per source = max_jobs / 5 roughly
        limit_per_source = max(2, request.max_jobs // 4)
        
        jobs = fetch_all_jobs(
            query=request.keywords,
            limit_per_source=limit_per_source
        )
        
        inserted = 0
        for job in jobs[:request.max_jobs + 5]: # Allow small buffer
            try:
                if not job.get("title") or not job.get("link"):
                    continue

                desc = job.get("description", "") or job.get("summary", "")
                insert_job(job, desc)
                inserted += 1
            except Exception as e:
                print(f"Failed to insert job: {e}")
                continue
        
        return {
            "message": f"Successfully scraped and added {inserted} jobs from 5+ sources",
            "count": inserted,
            "sources": list(set(j.get('source', 'Unknown') for j in jobs))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Health Check ==========

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ========== Initialize Database ==========

def init_database():
    """Initialize database with schema."""
    conn = get_db()
    with open("database/schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


if __name__ == "__main__":
    import uvicorn
    init_database()
    uvicorn.run(app, host="0.0.0.0", port=8000)
