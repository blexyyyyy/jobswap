from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.services.job_service import JobService
from app.schemas.job import JobOut

router = APIRouter()

@router.get("/feed", response_model=Dict[str, List[JobOut]])
async def get_job_feed(current_user: dict = Depends(get_current_user)):
    """Get job feed for the current user (excluding already swiped jobs)."""
    jobs = await JobService.get_feed(current_user)
    return {"jobs": jobs}

@router.get("/saved", response_model=Dict[str, List[JobOut]])
async def get_saved_jobs(current_user: dict = Depends(get_current_user)):
    """Get user's saved jobs."""
    return {"jobs": JobService.get_saved_jobs(current_user["id"])}

@router.get("/applied", response_model=Dict[str, List[JobOut]])
async def get_applied_jobs(current_user: dict = Depends(get_current_user)):
    """Get user's applied jobs."""
    return {"jobs": JobService.get_applied_jobs(current_user["id"])}
