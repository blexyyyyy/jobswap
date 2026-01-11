from typing import Dict, Any
from app.core.interfaces import MatchScorer
from ml.model import score_job

class LogisticMatchScorer:
    """
    Implementation of MatchScorer using Logistic Regression model.
    """
    def score(self, user_profile: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        return score_job(user_profile, job_data)
