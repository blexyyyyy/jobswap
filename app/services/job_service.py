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
            score = 50 + (overlap * 10)
            
            # Title match bonus
            if user_profile["preferred_seniority"] and user_profile["preferred_seniority"].lower() in job["title"].lower():
                score += 10
            
            job["match_score"] = min(95, score)
            job["logo_emoji"] = ["🚀", "💡", "📊", "🤖", "☁️", "🌱", "🏗️", "💰"][job["id"] % 8]
            processed_jobs.append(job)

        # Sort by heuristic score DESC
        processed_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        jobs = processed_jobs

        # === Parallel Explanation Generation ===
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
                
                # Run sync LLM call in thread pool
                print(f"[JobService] Fetching explanation for job: {job['title']}, user_skills: {user_profile['skills']}")
                explanation = await asyncio.to_thread(explanation_generator.generate_explanation, user_profile, job_summary)
                print(f"[JobService] Got explanation: {explanation}")
                job["match_explanation"] = explanation
                if explanation.get("match_score"):
                    job["match_score"] = explanation["match_score"]
            except Exception:
                # Fallback
                common_count = len(set(job["skills"]) & set(user_profile["skills"]))
                job["match_explanation"] = {
                    "match_reason": f"Matches {common_count} of your skills.",
                    "match_type": "neutral",
                    "match_score": 50 + (common_count * 10),
                    "missing_skills": [],
                    "career_tip": "Review requirements."
                }

        if jobs:
            await asyncio.gather(*[fetch_explanation(job) for job in jobs])
        
        return jobs

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
