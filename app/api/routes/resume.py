from fastapi import APIRouter, Depends, File, UploadFile
from app.api.deps import get_current_user
from app.services.user_service import UserService

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload and parse a resume."""
    return await UserService.process_resume(file, current_user["id"])
