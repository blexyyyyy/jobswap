from fastapi import APIRouter, Depends
from app.schemas.user import UserProfile, UserProfileOut
from app.api.deps import get_current_user
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=UserProfileOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    # UserService already has get_profile logic if needed, but current_user is already populated
    # by get_current_user dependency which queries DB.
    # To be perfectly clean, we could return current_user directly or re-fetch.
    # Returning current_user is fast.
    return current_user

@router.put("/update")
async def update_profile(profile: UserProfile, current_user: dict = Depends(get_current_user)):
    """Update user profile."""
    return UserService.update_profile(current_user["id"], profile)
