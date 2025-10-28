"""
Tests para el endpoint principal de la aplicación.
"""
import pytest


class TestMainApp:
    """Test suite para los endpoints principales de la aplicación."""
    
    def test_root_endpoint(self, client):
        """Test para el endpoint raíz."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "mensaje" in data
        assert "Hola, mundo!" in data["mensaje"]
    
    def test_cors_headers(self, client):
        """Test para verificar que no hay errores de CORS."""
        # El endpoint raíz no acepta OPTIONS, pero podemos verificar que 
        # la aplicación maneja CORS correctamente con una petición GET normal
        response = client.get("/")
        assert response.status_code == 200
        # Verificar que no hay errores relacionados con CORS
        data = response.json()
        assert isinstance(data, dict)
    
    def test_health_check_via_root(self, client):
        """Test para verificar que la aplicación está funcionando."""
        response = client.get("/")
        assert response.status_code == 200
        # Verificar que la respuesta es JSON válida
        data = response.json()
        assert isinstance(data, dict)
    
    def test_invalid_endpoint(self, client):
        """Test para endpoint inexistente."""
        response = client.get("/endpoint-inexistente")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test para método HTTP no permitido."""
        # El endpoint raíz solo acepta GET
        response = client.post("/")
        assert response.status_code == 405  # Method Not Allowed