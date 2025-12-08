from fastapi import APIRouter
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user."""
    return AuthService.register_user(user)

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """Login and get access token."""
    return AuthService.login_user(user)
