from fastapi import APIRouter, Depends
from app.schemas.job import SwipeAction
from app.api.deps import get_current_user
from app.services.swipe_service import SwipeService

router = APIRouter()

@router.post("")
async def record_swipe(swipe: SwipeAction, current_user: dict = Depends(get_current_user)):
    """Record a user's swipe action on a job."""
    return SwipeService.record_swipe(current_user["id"], swipe)
