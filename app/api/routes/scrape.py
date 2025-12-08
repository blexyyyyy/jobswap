from fastapi import APIRouter, Depends
from app.schemas.job import JobScrapeRequest
from app.api.deps import get_current_user
from app.services.job_service import JobService

router = APIRouter()

@router.post("/")
async def scrape_jobs(request: JobScrapeRequest, current_user: dict = Depends(get_current_user)):
    """Scrape jobs from multiple sources (Remotive, RemoteOK, etc.) and add to database."""
    result = JobService.scrape_jobs(request)
    return {
        "message": "Scraping completed",
        "meta": result
    }
