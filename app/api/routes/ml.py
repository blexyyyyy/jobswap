# app/api/routes/ml.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
try:
    from ml.train_logistic import main as train_model
    from ml.model import clear_cache
except ImportError:
    # Dummy fallbacks for Vercel/missing ML libs
    def train_model():
        raise HTTPException(status_code=501, detail="ML features not available (dependencies missing)")
    def clear_cache():
        pass
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def run_retraining():
    try:
        logger.info("[ML API] Starting retraining...")
        train_model()
        logger.info("[ML API] Retraining complete. Clearing cache.")
        clear_cache()
    except Exception as e:
        logger.error(f"[ML API] Retraining failed: {e}")

@router.post("/retrain")
async def retrain(background_tasks: BackgroundTasks):
    """
    Trigger model retraining in the background.
    """
    background_tasks.add_task(run_retraining)
    return {"message": "Retraining started in background."}
