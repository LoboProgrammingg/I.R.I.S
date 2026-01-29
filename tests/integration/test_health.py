"""Health endpoint integration tests."""

from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """Test /health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
