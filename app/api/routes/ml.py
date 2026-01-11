# app/api/routes/ml.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.ml_service import MLService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/retrain")
async def retrain(background_tasks: BackgroundTasks):
    """
    Trigger model retraining in the background.
    """
    background_tasks.add_task(MLService.run_retraining)
    return {"message": "Retraining started in background."}
