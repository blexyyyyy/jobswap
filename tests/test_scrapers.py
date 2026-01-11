import pytest
from unittest.mock import patch, MagicMock
from scrapers.unified_scraper import fetch_remoteok
from app.core.interfaces import JobResult

# Mock response data
MOCK_REMOTEOK_RESPONSE = [
    {"legal": "text"},
    {
        "position": "Senior Python Dev",
        "company": "Tech Corp",
        "location": "Remote",
        "tags": ["python", "senior"],
        "description": "<p>Job Description</p>",
        "url": "https://remoteok.com/job/123"
    }
]

@patch("requests.get")
def test_fetch_remoteok(mock_get):
    """
    Test RemoteOK scraper with mocked network response.
    Ensures correct parsing and data normalization.
    """
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REMOTEOK_RESPONSE
    mock_get.return_value = mock_response

    # Run scraper
    jobs = fetch_remoteok(query="python", limit=1)

    # Assertions
    assert len(jobs) == 1
    job = jobs[0]
    
    assert job["title"] == "Senior Python Dev"
    assert job["company"] == "Tech Corp"
    assert job["source"] == "RemoteOK"
    assert "python" in job["skills"]
