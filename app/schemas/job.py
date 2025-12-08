from typing import Optional
from pydantic import BaseModel

class SwipeAction(BaseModel):
    job_id: int
    action: str  # 'apply', 'skip', 'save'

class JobScrapeRequest(BaseModel):
    keywords: str
    location: Optional[str] = "India"
    max_jobs: Optional[int] = 10
from typing import List, Any

class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    skills: Optional[List[str]] = []  # List of strings, parsed from DB string
    description: Optional[str] = None
    source_url: Optional[str] = None
    match_score: Optional[int] = 0
    match_explanation: Optional[Any] = None # Dict or JSON object
    logo_emoji: Optional[str] = "💼"
    class Config:
        from_attributes = True
