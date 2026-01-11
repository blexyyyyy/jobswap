import pytest
import sys
import os

# Ensure app is in path
sys.path.append(os.getcwd())

import pytest
import sys
import os

# Ensure app is in path
sys.path.append(os.getcwd())

# We try to import the scoring function. 
# If it doesn't exist yet (as per original repo state), we skip or fail gracefully.
# Assuming 'ml.model' exists based on imports seen in job_service.py

def test_ml_scoring_pure():
    """
    Test the ML scoring function with fixed inputs.
    """
    try:
        from ml.model import score_job
    except ImportError:
        pytest.skip("ML model module not found")

    user_profile = {
        "skills": ["python", "fastapi"],
        "experience_years": 5,
        "preferred_location": "Remote",
        "preferred_seniority": "Senior",
        "resume_text": "Python developer with 5 years experience."
    }
    
    job = {
        "id": 1,
        "title": "Senior Python Developer",
        "description": "We need a Python expert.",
        "skills": ["python", "django"],
        "location": "Remote",
        "job_type": "Full-time"
    }
    
    # Score should be a float between 0 and 1
    score = score_job(user_profile, job)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
