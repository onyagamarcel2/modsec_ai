"""
Tests unitaires pour l'application FastAPI.
"""

import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
from src.app import app

@pytest.fixture
def client():
    """Crée un client de test pour l'application."""
    return TestClient(app)

def test_health_check(client):
    """Test le endpoint de vérification de santé."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_logs(client):
    """Test l'analyse des logs."""
    test_logs = [
        "GET /admin HTTP/1.1",
        "User-Agent: sqlmap/1.4.12"
    ]
    
    response = client.post("/analyze", json={"logs": test_logs})
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    assert "score" in data

class TestModSecAPI:
    """Tests pour l'API ModSec."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Configure les tests."""
        self.client = TestClient(app)
        
        # Créer des données de test
        self.sample_log = {
            "timestamp": "2024-01-26T10:00:00",
            "client_ip": "192.168.1.1",
            "request_uri": "/api/test",
            "message": "Test message [file \"/etc/modsecurity/rules/test.conf\"] [line \"1\"] [id \"1000\"] [severity \"CRITICAL\"]"
        }
        
        self.sample_logs = [self.sample_log] * 3

    def test_detect_anomaly_single(self):
        """Test single log anomaly detection endpoint."""
        response = self.client.post("/detect", json=self.sample_log)
        assert response.status_code == 200
        
        data = response.json()
        assert "is_anomaly" in data
        assert "anomaly_score" in data
        assert isinstance(data["is_anomaly"], bool)
        assert isinstance(data["anomaly_score"], float)

    def test_detect_anomaly_batch(self):
        """Test batch log anomaly detection endpoint."""
        response = self.client.post("/detect/batch", json=self.sample_logs)
        assert response.status_code == 200
        
        data = response.json()
        assert "anomalies" in data
        assert isinstance(data["anomalies"], list)
        assert len(data["anomalies"]) == len(self.sample_logs)

    def test_get_anomaly_stats(self):
        """Test anomaly statistics endpoint."""
        response = self.client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_logs" in data
        assert "total_anomalies" in data
        assert "anomaly_rate" in data
        assert isinstance(data["total_logs"], int)
        assert isinstance(data["total_anomalies"], int)
        assert isinstance(data["anomaly_rate"], float)

    def test_invalid_log_format(self):
        """Test handling invalid log format."""
        invalid_log = {
            "timestamp": "invalid",
            "client_ip": "invalid",
            "request_uri": "invalid",
            "message": "invalid"
        }
        
        response = self.client.post("/detect", json=invalid_log)
        assert response.status_code == 422

    def test_missing_required_fields(self):
        """Test handling missing required fields."""
        incomplete_log = {
            "timestamp": "2024-01-26T10:00:00",
            "client_ip": "192.168.1.1"
            # Missing request_uri and message
        }
        
        response = self.client.post("/detect", json=incomplete_log)
        assert response.status_code == 422

    def test_invalid_batch_format(self):
        """Test handling invalid batch format."""
        invalid_batch = "not a list"
        
        response = self.client.post("/detect/batch", json=invalid_batch)
        assert response.status_code == 422

    def test_empty_batch(self):
        """Test handling empty batch."""
        empty_batch = []
        
        response = self.client.post("/detect/batch", json=empty_batch)
        assert response.status_code == 200
        
        data = response.json()
        self.assertEqual(len(data["anomalies"]), 0)

if __name__ == '__main__':
    pytest.main() 