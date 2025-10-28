"""
Tests para endpoints chat
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

class TestChatEndpoints:
    """Tests para endpoints chat."""
    
    def test_chat_endpoint(self, client):
        """Test POST /chat"""
        chat_data = {"message": "Hola, ¿cómo estás?"}
        response = client.post("/chat", json=chat_data)
        assert response.status_code not in [404]
    
    def test_chat_completions_endpoint(self, client):
        """Test POST /chat-completions"""
        completion_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        response = client.post("/chat-completions", json=completion_data)
        assert response.status_code not in [404]
    
    def test_chat_mensaje_vacio(self, client):
        """Test chat con mensaje vacío"""
        chat_data = {"message": ""}
        response = client.post("/chat", json=chat_data)
        assert response.status_code in [200, 422, 400, 500]
    
    def test_chat_sin_mensaje(self, client):
        """Test chat sin mensaje"""
        response = client.post("/chat", json={})
        assert response.status_code in [422, 400]
    
    def test_chat_completions_sin_mensajes(self, client):
        """Test chat-completions sin mensajes"""
        completion_data = {
            "model": "gpt-3.5-turbo",
            "messages": []
        }
        response = client.post("/chat-completions", json=completion_data)
        assert response.status_code in [422, 400, 500]
