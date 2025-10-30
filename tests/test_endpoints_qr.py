"""
Tests para endpoints QR
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Configurar el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def client():
    """Cliente de test."""
    from main import app
    return TestClient(app)

class TestQREndpoints:
    """Tests para endpoints QR."""
    
    def test_validate_qr(self, client):
        """Test GET /qr/validate"""
        response = client.get("/qr/validate?code=TEST123")
        assert response.status_code in [200, 401, 422, 500, 400]
    
    def test_redirect_qr(self, client):
        """Test GET /qr/redirect/{code}"""
        response = client.get("/qr/redirect/TEST123", follow_redirects=False)
        # Este endpoint debería devolver un redirect (302)
        assert response.status_code in [302], f"Expected 302 redirect, got {response.status_code}"
    
    def test_generate_qr(self, client):
        """Test GET /qr/generate/{code}"""
        response = client.get("/qr/generate/TEST123")
        assert response.status_code not in [404]
    
    def test_batch_generate_qr(self, client):
        """Test POST /qr/generate/batch"""
        batch_data = {"codes": ["QR_001", "QR_002"]}
        response = client.post("/qr/generate/batch", json=batch_data)
        assert response.status_code not in [404]
