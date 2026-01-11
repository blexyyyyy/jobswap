from app.core.logging import logger

try:
    from ml.train_logistic import main as train_model
    from ml.model import clear_cache
except ImportError:
    # Fallback for environments without ML deps
    def train_model():
        logger.warning("ML dependencies missing. Skipping training.")
    def clear_cache():
        pass

class MLService:
    @staticmethod
    def run_retraining():
        """
        Orchestrates the model retraining process.
        """
        try:
            logger.info("[MLService] Starting retraining...")
            train_model()
            logger.info("[MLService] Retraining complete. Clearing cache.")
            clear_cache()
            return True
        except Exception as e:
            logger.error(f"[MLService] Retraining failed: {e}")
            raise e
