from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_moderate_text():
    response = client.post("/api/v1/moderate/text", json={"text": "test message"})
    assert response.status_code == 200
    assert "message" in response.json()
