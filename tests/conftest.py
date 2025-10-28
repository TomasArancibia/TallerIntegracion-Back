"""
Configuración básica de tests - Solo fixtures esenciales
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient

# Configurar el path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def client():
    """Cliente básico de FastAPI para tests."""
    from main import app
    return TestClient(app)
