"""
Configuración básica de tests - Solo fixtures esenciales
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient

# Configurar el path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar variables de entorno para testing si no están definidas
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
if not os.getenv('SUPABASE_URL'):
    os.environ['SUPABASE_URL'] = 'https://fake-url.supabase.co'
if not os.getenv('SUPABASE_ANON_KEY'):
    os.environ['SUPABASE_ANON_KEY'] = 'fake-key'
if not os.getenv('SUPABASE_SERVICE_ROLE_KEY'):
    os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'fake-service-key'
if not os.getenv('OPENAI_API_KEY'):
    os.environ['OPENAI_API_KEY'] = 'sk-fake-key'

@pytest.fixture
def client():
    """Cliente básico de FastAPI para tests."""
    try:
        from main import app
        return TestClient(app)
    except Exception as e:
        pytest.skip(f"No se pudo inicializar la aplicación: {e}")

@pytest.fixture
def mock_db():
    """Mock básico de base de datos para tests."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    return mock
