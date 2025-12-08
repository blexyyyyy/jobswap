from app.schemas.job import SwipeAction
from database.connection import get_db_connection
from fastapi import HTTPException

class SwipeService:
    @staticmethod
    def record_swipe(user_id: int, swipe: SwipeAction):
        if swipe.action not in ("apply", "skip", "save"):
            raise HTTPException(status_code=400, detail="Invalid action")
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO user_swipes (user_id, job_id, action) VALUES (?, ?, ?)",
                    (user_id, swipe.job_id, swipe.action)
                )
                conn.commit()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        return {"message": f"Recorded {swipe.action} for job {swipe.job_id}"}
