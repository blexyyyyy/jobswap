from fastapi import APIRouter, Depends
from app.schemas.chat import ChatMessage
from app.api.deps import get_current_user
from app.services.chat_service import ChatService

router = APIRouter()

@router.get("/{job_id}")
async def get_chat_messages(job_id: int, current_user: dict = Depends(get_current_user)):
    """Get all chat messages for a job application."""
    return {"messages": ChatService.get_messages(current_user["id"], job_id)}


@router.post("/{job_id}")
async def send_message(job_id: int, msg: ChatMessage, current_user: dict = Depends(get_current_user)):
    """Send a message to employer."""
    return ChatService.send_message(current_user["id"], job_id, msg)
