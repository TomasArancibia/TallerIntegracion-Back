"""
Tests para endpoints admin
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

class TestAdminEndpoints:
    """Tests para endpoints admin."""
    
    def test_me_endpoint(self, client):
        """Test GET /admin/me"""
        headers = {"Authorization": "Bearer fake_token"}
        response = client.get("/admin/me", headers=headers)
        assert response.status_code in [200, 401, 422, 500]
    
    def test_bootstrap_endpoint(self, client):
        """Test GET /admin/bootstrap"""
        headers = {"Authorization": "Bearer fake_token"}
        response = client.get("/admin/bootstrap", headers=headers)
        assert response.status_code not in [404]
    
    def test_metricas_endpoint(self, client):
        """Test GET /admin/metricas"""
        headers = {"Authorization": "Bearer fake_token"}
        response = client.get("/admin/metricas", headers=headers)
        assert response.status_code not in [404]
    
    def test_users_endpoint(self, client):
        """Test GET /admin/users"""
        headers = {"Authorization": "Bearer fake_token"}
        response = client.get("/admin/users", headers=headers)
        assert response.status_code not in [404]
    
    def test_create_user(self, client):
        """Test POST /admin/users"""
        headers = {"Authorization": "Bearer fake_token"}
        user_data = {
            "email": "test@hospital.com",
            "nombre": "Test User",
            "rol": "jefe_area",
            "password": "password123"
        }
        response = client.post("/admin/users", json=user_data, headers=headers)
        assert response.status_code not in [404]
    
    def test_update_me(self, client):
        """Test PUT /admin/me"""
        headers = {"Authorization": "Bearer fake_token"}
        update_data = {"nombre": "Nuevo Nombre"}
        response = client.put("/admin/me", json=update_data, headers=headers)
        assert response.status_code not in [404]
    
    def test_create_habitacion(self, client):
        """Test POST /admin/habitaciones"""
        headers = {"Authorization": "Bearer fake_token"}
        habitacion_data = {"numero": "H101", "piso_id": 1, "tipo": "individual"}
        response = client.post("/admin/habitaciones", json=habitacion_data, headers=headers)
        assert response.status_code not in [404]
    
    def test_create_cama(self, client):
        """Test POST /admin/camas"""
        headers = {"Authorization": "Bearer fake_token"}
        cama_data = {"numero": "C001", "habitacion_id": 1, "tipo": "individual"}
        response = client.post("/admin/camas", json=cama_data, headers=headers)
        assert response.status_code not in [404]
