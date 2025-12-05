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

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (int(payload["sub"]),))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return dict(user)


# ========== Auth Endpoints ==========

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    password_hash = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
        (user.email, password_hash, user.name)
    )
    conn.commit()
    user_id = cursor.lastrowid
    
    conn.close()
    
    # Generate token
    token = create_access_token(user_id, user.email)
    
    return TokenResponse(
        access_token=token,
        user={"id": user_id, "email": user.email, "name": user.name}
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """Login and get access token."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()
    
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
    conn = get_db()
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
    conn.close()
    
    return {"message": "Profile updated successfully"}


# ========== Jobs Endpoints ==========

@app.get("/api/jobs/feed")
async def get_job_feed(current_user: dict = Depends(get_current_user)):
    """Get job feed for the current user (excluding already swiped jobs)."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get jobs not yet swiped by user
    cursor.execute("""
        SELECT j.* FROM jobs j
        WHERE j.id NOT IN (
            SELECT job_id FROM user_swipes WHERE user_id = ?
        )
        ORDER BY j.created_at DESC
        LIMIT 20
    """, (current_user["id"],))
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Format jobs for frontend
    from matching.explanations import explanation_generator
    
    # Get user profile for matching
    user_profile = {
        "skills": current_user["skills"].split(",") if current_user["skills"] else [],
        "experience_years": current_user["experience_years"],
        "preferred_location": current_user["preferred_location"],
        "preferred_seniority": current_user["preferred_seniority"],
        "resume_text": current_user["resume_text"]
    }

    for job in jobs:
        # Convert skills from string to array
        if job.get("skills"):
            job["skills"] = [s.strip() for s in job["skills"].split(",")]
        else:
            job["skills"] = []
        
        # Add match score and explanation (mock/lightweight for feed, could be pre-calculated)
        # Note: calling LLM for 20 jobs might be slow, for now using a lightweight heuristic or cached explanation
        # For this MVP, we will stick to the heuristic score but add a placeholder for explanation
        # that the frontend can fetch on demand or we accept the latency for "premium" feel.
        # Let's use the heuristic but enrich it if we had the compute.
        
        job["match_score"] = 75 + (hash(job["title"]) % 20)
        job["logo_emoji"] = ["🚀", "💡", "📊", "🤖", "☁️", "🌱", "🏗️", "💰"][job["id"] % 8]
        
        # Use Gemini to generate explanation
        try:
            # Prepare minimal job data for LLM to save tokens/latency
            job_summary = {
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "skills": job["skills"],
                "description": job["description"][:500] if job["description"] else ""
            }
            
            explanation = explanation_generator.generate_explanation(user_profile, job_summary)
            job["match_explanation"] = explanation
            
            # Update match score based on LLM assessment if available, otherwise keep heuristic
            if explanation.get("match_score"):
                job["match_score"] = explanation["match_score"]
                
        except Exception as e:
            print(f"Error generating explanation for job {job['id']}: {e}")
            # Fallback to heuristic if LLM fails
            common_count = len(set(job["skills"]) & set(user_profile["skills"]))
            job["match_explanation"] = {
                "match_reason": f"Matches {common_count} of your skills.",
                "match_type": "neutral",
                "missing_skills": []
            }
    
    return {"jobs": jobs}


@app.post("/api/swipe")
async def record_swipe(swipe: SwipeAction, current_user: dict = Depends(get_current_user)):
    """Record a user's swipe action on a job."""
    if swipe.action not in ("apply", "skip", "save"):
        raise HTTPException(status_code=400, detail="Invalid action")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO user_swipes (user_id, job_id, action) VALUES (?, ?, ?)",
            (current_user["id"], swipe.job_id, swipe.action)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    
    conn.close()
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
    """Scrape jobs from TimesJobs and add to database."""
    try:
        from scrapers.timesjobs_scraper import fetch_timesjobs
        from database.db_manager import insert_job
        
        # Scrape jobs
        jobs = fetch_timesjobs(
            keywords=request.keywords,
            location=request.location,
            max_pages=min(request.max_jobs // 10, 3)  # 10 jobs per page
        )
        
        # Insert into database
        inserted = 0
        for job in jobs[:request.max_jobs]:
            try:
                insert_job(job, job.get("summary", ""))
                inserted += 1
            except Exception:
                continue
        
        return {
            "message": f"Successfully scraped and added {inserted} jobs",
            "count": inserted
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
