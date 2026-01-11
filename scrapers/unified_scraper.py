
import requests
import feedparser
from typing import List, Dict, Any, Optional
import time
import random

from app.core.logging import logger

from app.core.resilience import retry_external_api

# Unified Scraper for multiple sources

@retry_external_api
def fetch_remoteok(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch jobs from RemoteOK API."""
    logger.info(f"Fetching from RemoteOK: {query}")
    url = "https://remoteok.com/api"
    # RemoteOK filters by tag if provided
    params = {}
    if query:
        params['tag'] = query.lower()
    
    try:
        # User-Agent is often required
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # First element is legal text, skip it
            jobs = data[1:] if len(data) > 0 else []
            
            normalized = []
            for job in jobs[:limit]:
                normalized.append({
                    "title": job.get("position", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", "Remote"),
                    "skills": ", ".join(job.get("tags", [])),
                    "summary": job.get("description", "")[:500], # Description is HTML, might need cleaning
                    "source_url": job.get("url", ""),
                    "source": "RemoteOK"
                })
            return normalized
    except Exception as e:
        logger.error(f"Error fetching RemoteOK: {e}")
        # Re-raise for retry logic to catch it, unless we really want to just fail silently.
        # But wait, the original code returned [] and logged.
        # Retry decorator expects an exception. 
        # If I catch and return [], retry won't trigger!
        # I should raise e here if I want retry.
        raise e
    return []

@retry_external_api
def fetch_arbeitnow(query: str, limit: int = 10) -> List[Dict[str, Any]]:
   # ... (content will serve as target match)
    """Fetch jobs from Arbeitnow API."""
    logger.info(f"Fetching from Arbeitnow: {query}")
    url = "https://arbeitnow.com/api/job-board-api"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("data", [])
            
            # Simple keyword filtering since API doesn't support search query params directly in free tier easily
            filtered = []
            for job in jobs:
                if not query or query.lower() in job.get("title", "").lower() or query.lower() in job.get("tags", []):
                    filtered.append(job)
            
            normalized = []
            for job in filtered[:limit]:
                normalized.append({
                    "title": job.get("title", ""),
                    "company": job.get("company_name", ""),
                    "location": job.get("location", "Remote"),
                    "skills": ", ".join(job.get("tags", [])),
                    "summary": job.get("description", "")[:500], # HTML
                    "source_url": job.get("url", ""),
                    "source": "Arbeitnow"
                })
            return normalized
    except Exception as e:
        logger.error(f"Error fetching Arbeitnow: {e}")
        raise e
    return []

@retry_external_api
def fetch_weworkremotely(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch jobs from WeWorkRemotely RSS."""
    logger.info(f"Fetching from WeWorkRemotely: {query}")
    # RSS Feed categories: programming, design, etc.
    # We'll just fetch the 'All' feed or Programming
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    
    try:
        feed = feedparser.parse(url)
        normalized = []
        
        for entry in feed.entries:
            # Simple soft filter
            if query and query.lower() not in entry.title.lower() and query.lower() not in entry.summary.lower():
                continue
                
            normalized.append({
                "title": entry.title,
                "company": entry.get("author", "Unknown"), # Often in title "Company: Role"
                "location": "Remote",
                "skills": query if query else "Remote",
                "summary": entry.summary[:500],
                "source_url": entry.link,
                "source": "WeWorkRemotely"
            })
            if len(normalized) >= limit:
                break
        return normalized
    except Exception as e:
        logger.error(f"Error fetching WeWorkRemotely: {e}")
        raise e
    return []

@retry_external_api
def fetch_jobicy(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch jobs from Jobicy RSS."""
    logger.info(f"Fetching from Jobicy: {query}")
    url = "https://jobicy.com/feed/dev"
    
    try:
        feed = feedparser.parse(url)
        normalized = []
        
        for entry in feed.entries:
             if query and query.lower() not in entry.title.lower():
                continue

             normalized.append({
                "title": entry.title,
                "company": "See Link",
                "location": "Remote",
                "skills": "Remote",
                "summary": entry.summary[:500],
                "source_url": entry.link,
                "source": "Jobicy"
            })
             if len(normalized) >= limit:
                break
        return normalized
    except Exception as e:
        logger.error(f"Error fetching Jobicy: {e}")
        raise e
    return []    

@retry_external_api
def fetch_remotive(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch jobs from Remotive API."""
    logger.info(f"Fetching from Remotive: {query}")
    url = "https://remotive.com/api/remote-jobs"
    params = {}
    if query:
        params["search"] = query
        
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            
            normalized = []
            for job in jobs[:limit]:
                normalized.append({
                    "title": job.get("title", ""),
                    "company": job.get("company_name", ""),
                    "location": job.get("candidate_required_location", "Remote"),
                    "skills": ", ".join(job.get("tags", [])),
                    "summary": job.get("description", "")[:500], # HTML
                    "source_url": job.get("url", ""),
                    "source": "Remotive"
                })
            return normalized
    except Exception as e:
        logger.error(f"Error fetching Remotive: {e}")
        raise e
    return []

def fetch_all_jobs(query: str, limit_per_source: int = 5) -> List[Dict[str, Any]]:
    """Aggregate jobs from all sources."""
    all_jobs = []
    
    # 1. Remotive (High Quality)
    all_jobs.extend(fetch_remotive(query, limit_per_source))
    
    # 2. RemoteOK
    all_jobs.extend(fetch_remoteok(query, limit_per_source))
    
    # 3. Arbeitnow
    all_jobs.extend(fetch_arbeitnow(query, limit_per_source))
    
    # 4. WeWorkRemotely
    all_jobs.extend(fetch_weworkremotely(query, limit_per_source))
    
    # 5. Jobicy
    all_jobs.extend(fetch_jobicy(query, limit_per_source))
    
    # Shuffle to mix sources
    random.shuffle(all_jobs)
    
    return all_jobs

if __name__ == "__main__":
    # Test
    results = fetch_all_jobs("python", 2)
    print(f"Found {len(results)} jobs")
    for job in results:
        print(f"[{job['source']}] {job['title']} at {job['company']}")
