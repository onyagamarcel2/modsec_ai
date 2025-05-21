"""
Tests unitaires pour l'API FastAPI.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Test de l'endpoint /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_logs(client):
    """Test de l'endpoint /analyze avec des logs valides."""
    test_logs = [
        "GET /api/users HTTP/1.1",
        "POST /api/login HTTP/1.1",
        "GET /api/products HTTP/1.1"
    ]
    
    response = client.post("/analyze", json={"logs": test_logs})
    assert response.status_code == 200
    
    data = response.json()
    assert "anomalies" in data
    assert "score" in data
    assert len(data["anomalies"]) == len(test_logs)
    
    # Vérifier la structure de chaque anomalie
    for anomaly in data["anomalies"]:
        assert "log" in anomaly
        assert "score" in anomaly
        assert "is_anomaly" in anomaly
        assert isinstance(anomaly["score"], float)
        assert isinstance(anomaly["is_anomaly"], bool)

def test_analyze_empty_logs(client):
    """Test de l'endpoint /analyze avec une liste vide de logs."""
    response = client.post("/analyze", json={"logs": []})
    assert response.status_code == 200
    
    data = response.json()
    assert data["anomalies"] == []
    assert data["score"] == 0.0

def test_analyze_invalid_request(client):
    """Test de l'endpoint /analyze avec une requête invalide."""
    # Test sans le champ 'logs'
    response = client.post("/analyze", json={})
    assert response.status_code == 422
    
    # Test avec un type invalide pour les logs
    response = client.post("/analyze", json={"logs": "not a list"})
    assert response.status_code == 422

def test_analyze_large_input(client):
    """Test de l'endpoint /analyze avec un grand nombre de logs."""
    large_logs = ["GET /test HTTP/1.1"] * 1000
    response = client.post("/analyze", json={"logs": large_logs})
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["anomalies"]) == 1000
    assert isinstance(data["score"], float)

if __name__ == '__main__':
    pytest.main() 