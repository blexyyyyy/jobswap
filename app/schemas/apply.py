from typing import List, Optional
from pydantic import BaseModel, EmailStr


class ApplyRequest(BaseModel):
    job_ids: List[int]
    override_email: Optional[EmailStr] = None  # fallback if no job/company email yet


class ApplyResponse(BaseModel):
    queued: int
    already_queued: int
    failed: int
