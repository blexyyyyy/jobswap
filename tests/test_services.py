import pytest
from app.services.ml_service import MLService
from ml.scorer import LogisticMatchScorer

def test_logistic_scorer():
    """Test the scorer class wrapper."""
    scorer = LogisticMatchScorer()
    
    user_profile = {
        "skills": ["python"],
        "experience_years": 5,
        "preferred_location": "Remote",
        "preferred_seniority": "Senior",
        "resume_text": "Python dev"
    }
    job = {
        "id": 1,
        "title": "Python Dev",
        "skills": ["python"],
        "description": "text",
        "location": "Remote"
    }
    
    score = scorer.score(user_profile, job)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

def test_ml_service_structure():
    """Verify MLService has required methods."""
    assert hasattr(MLService, 'run_retraining')
