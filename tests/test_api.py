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
    # Verify each model has required fields
    for model in data["models"]:
        assert "id" in model
        assert "name" in model
        assert "provider" in model
    # Check at least one known model is present
    model_ids = [m["id"] for m in data["models"]]
    assert any("anthropic" in mid or "meta" in mid or "mistral" in mid for mid in model_ids)

def test_get_agent_roles():
    response = client.get("/api/v1/agents/roles")
    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert len(data["roles"]) > 0
    role_ids = [r["id"] for r in data["roles"]]
    assert "product_manager" in role_ids
    assert "engineer" in role_ids
