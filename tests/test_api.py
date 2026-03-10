import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_api_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]

def test_get_models():
    response = client.get("/api/v1/models/bedrock")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    # Check if our fallback models or enum models are present
    model_ids = [m["id"] for m in data["models"]]
    assert "us.amazon.nova-pro-v1:0" in model_ids or "us.anthropic.claude-sonnet-4-20250514-v1:0" in model_ids

def test_get_agent_roles():
    response = client.get("/api/v1/agents/roles")
    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert len(data["roles"]) > 0
    role_ids = [r["id"] for r in data["roles"]]
    assert "product_manager" in role_ids
    assert "engineer" in role_ids
