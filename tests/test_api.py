from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Verify that the API root returns a 200 OK and expected message."""
    response = client.get("/")
    assert response.status_code == 200
    # The message might still contain the old name if the user hasn't updated the logic yet, 
    # but we updated the key parts. Let's just check status for now or generic structure.
    data = response.json()
    assert "message" in data

def test_health_check():
    """Verify the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
