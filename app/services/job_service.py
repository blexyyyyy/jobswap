from database.connection import get_db_connection
from app.schemas.job import JobScrapeRequest
import asyncio

class JobService:
    @staticmethod
    async def get_feed(user: dict):
        user_id = user["id"]
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
                """, (user_id,))
                
                all_jobs = [dict(row) for row in cursor.fetchall()]
            
            # Use matching logic to sort and explain
            return await JobService._process_jobs(all_jobs, user)

        except Exception as e:
            # Log error
            raise e

    @staticmethod
    async def _process_jobs(all_jobs, current_user):
        """Process jobs with ML scoring only. Explanations are fetched on-demand."""
        
        user_profile = {
            "skills": current_user["skills"].split(",") if current_user["skills"] else [],
            "experience_years": current_user["experience_years"],
            "preferred_location": current_user["preferred_location"],
            "preferred_seniority": current_user["preferred_seniority"],
            "resume_text": current_user["resume_text"]
        }

        processed_jobs = []
        for job in all_jobs:
            # Convert skills from string to array
            if job.get("skills"):
                job["skills"] = [s.strip() for s in job["skills"].split(",")]
            else:
                job["skills"] = []
                
            # === ML Scoring ===
            # === ML Scoring ===
            try:
                from ml.model import score_job
                # Get probability (0.0 to 1.0)
                prob = score_job(user_profile, job)
                job["match_score"] = int(prob * 100)
            except ImportError:
                job["match_score"] = 0 # Default score if ML missing
            
            job["logo_emoji"] = ["🚀", "💡", "📊", "🤖", "☁️", "🌱", "🏗️", "💰"][job["id"] % 8]
            
            # NO explanation generated upfront - set to null
            job["match_explanation"] = None
            
            processed_jobs.append(job)

        # Sort by ML match score DESC
        processed_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return processed_jobs

    @staticmethod
    async def get_explanation(job_id: int, user: dict):
        """Generate explanation for a specific job on-demand."""
        import asyncio
        from matching.explanations import explanation_generator
        from ml.features import extract_job_features
        
        user_profile = {
            "skills": user["skills"].split(",") if user["skills"] else [],
            "experience_years": user["experience_years"],
            "preferred_location": user["preferred_location"],
            "preferred_seniority": user["preferred_seniority"],
            "resume_text": user["resume_text"] or "Not provided"
        }
        
        # Fetch job from DB
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return {"error": "Job not found"}
            job = dict(row)
        
        # Parse skills
        if job.get("skills"):
            job["skills"] = [s.strip() for s in job["skills"].split(",")]
        else:
            job["skills"] = []
        
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
        
        # ML scoring
        # ML scoring
        try:
            from ml.model import score_job
            prob = score_job(user_profile, job)
            ml_score = int(prob * 100)
        except ImportError:
            ml_score = 0
        
        # ML features
        try:
            from ml.features import extract_job_features
            ml_features = extract_job_features(user_profile, job)
        except ImportError:
            ml_features = {}
        
        job_summary = {
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "skills": job["skills"],
            "description": job["description"],
            "ml_score": ml_score,
            "ml_features": ml_features
        }
        
        # Generate explanation
        print(f"[JobService] On-demand explanation for job {job_id}: {job['title']}")
        explanation = await asyncio.to_thread(explanation_generator.generate_explanation, user_profile, job_summary)
        
        if not explanation:
            # This should technically be handled by ExplanationGenerator, but check again
            return {"match_reason": "Analysis unavailable at the moment.", "match_type": "medium"}
            
        return explanation


    @staticmethod
    def get_saved_jobs(user_id: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT j.* FROM jobs j
                JOIN user_swipes us ON j.id = us.job_id
                WHERE us.user_id = ? AND us.action = 'save'
                ORDER BY us.created_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_applied_jobs(user_id: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT j.* FROM jobs j
                JOIN user_swipes us ON j.id = us.job_id
                WHERE us.user_id = ? AND us.action = 'apply'
                ORDER BY us.created_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def scrape_jobs(request: JobScrapeRequest):
        from scrapers.runner import fetch_all_sources
        from database.db_manager import insert_job_if_new
        
        # Limit per source
        max_jobs = request.max_jobs or 20
        per_source = max(5, max_jobs // 3)
        
        normalized_jobs = fetch_all_sources(query=request.keywords, max_jobs_per_source=per_source)
        
        inserted = 0
        for job in normalized_jobs[:max_jobs + 10]: 
            if insert_job_if_new(job):
                inserted += 1
        
        return {
            "message": f"Successfully scraped {len(normalized_jobs)} and inserted {inserted} new jobs.",
            "requested": max_jobs,
            "scraped": len(normalized_jobs),
            "inserted": inserted,
            "sources": list(set(j.get('source', 'Unknown') for j in normalized_jobs))
        }
