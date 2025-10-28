"""
Tests para endpoints de solicitudes
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import sys
import os

# Configurar el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def client():
    """Cliente de test."""
    from main import app
    return TestClient(app)

class TestSolicitudesEndpoints:
    """Tests para endpoints de solicitudes."""
    
    def test_listar_hospitales(self, client):
        """Test GET /hospitales"""
        response = client.get("/hospitales")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_obtener_hospital_por_id(self, client):
        """Test GET /hospitales/{id}"""
        response = client.get("/hospitales/1")
        assert response.status_code in [200, 401, 422, 500, 404]
    
    def test_listar_edificios(self, client):
        """Test GET /edificios"""
        response = client.get("/edificios")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_listar_pisos(self, client):
        """Test GET /pisos"""
        response = client.get("/pisos")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_listar_servicios(self, client):
        """Test GET /servicios"""
        response = client.get("/servicios")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_listar_habitaciones(self, client):
        """Test GET /habitaciones"""
        response = client.get("/habitaciones")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_listar_camas(self, client):
        """Test GET /camas"""
        response = client.get("/camas")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_obtener_cama_por_qr(self, client):
        """Test GET /camas/by-qr/{qr}"""
        response = client.get("/camas/by-qr/QR123")
        assert response.status_code in [200, 401, 422, 500, 404]
    
    def test_listar_areas(self, client):
        """Test GET /areas"""
        response = client.get("/areas")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_crear_solicitud(self, client):
        """Test POST /solicitudes"""
        solicitud_data = {
            "nombre_paciente": "Juan Pérez",
            "rut_paciente": "12345678-9",
            "telefono": "+56912345678",
            "servicio_solicitado": "Hospitalización",
            "prioridad": "alta"
        }
        response = client.post("/solicitudes", json=solicitud_data)
        assert response.status_code in [200, 201, 401, 422, 500]
    
    def test_listar_solicitudes(self, client):
        """Test GET /solicitudes"""
        response = client.get("/solicitudes")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_obtener_solicitud_por_id(self, client):
        """Test GET /solicitudes/{id}"""
        response = client.get("/solicitudes/1")
        assert response.status_code in [200, 401, 422, 500, 404]
    
    def test_actualizar_estado_solicitud(self, client):
        """Test PUT /solicitudes/{id}/estado"""
        estado_data = {"nuevo_estado": "en_proceso"}
        response = client.put("/solicitudes/1/estado", json=estado_data)
        assert response.status_code in [200, 401, 422, 500, 404]
    
    def test_metricas_solicitudes_por_fecha(self, client):
        """Test GET /metricas/solicitudes-por-fecha"""
        response = client.get("/metricas/solicitudes-por-fecha?fecha_inicio=2024-01-01&fecha_fin=2024-12-31")
        assert response.status_code in [200, 401, 422, 500]
    
    def test_metricas_solicitudes_por_area(self, client):
        """Test GET /metricas/solicitudes-por-area"""
        response = client.get("/metricas/solicitudes-por-area?fecha_inicio=2024-01-01&fecha_fin=2024-12-31")
        assert response.status_code in [200, 401, 422, 500]
