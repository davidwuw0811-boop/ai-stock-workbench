from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_screening_us():
    response = client.post(
        "/api/screening",
        json={
            "market": "US",
            "strategies": ["fundamental", "momentum", "sentiment"],
            "risk_profile": "balanced",
            "top_n": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["market"] == "US"
    assert len(data["results"]) == 3
    assert "overall_score" in data["results"][0]
