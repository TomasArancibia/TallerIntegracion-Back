# Guía de Configuración y Ejecución de Tests

## 🚀 Instalación Rápida

### 1. Instalar Dependencias
```bash
# Dependencias principales
pip install -r requirements.txt

# Dependencias de testing
pip install -r requirements-test.txt
```

### 2. Ejecutar Tests
```bash
# Opción 1: Usar el script (recomendado)
chmod +x run_tests.sh
./run_tests.sh

# Opción 2: Usar pytest directamente
pytest

# Opción 3: Con cobertura
pytest --cov=. --cov-report=html
```

## 📋 Comandos Disponibles

### Tests Básicos
```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_solicitudes.py
pytest tests/test_qr.py
pytest tests/test_admin.py

# Un test específico
pytest tests/test_solicitudes.py::TestSolicitudesRouter::test_crear_solicitud
```

### Tests con Opciones
```bash
# Verbose (más detalles)
pytest -v

# Parar en primer error
pytest -x

# Ejecutar en paralelo
pytest -n auto

# Solo tests rápidos
pytest -m "not slow"
```

### Cobertura
```bash
# Cobertura básica
pytest --cov=.

# Cobertura con reporte HTML
pytest --cov=. --cov-report=html

# Cobertura con detalles de líneas faltantes
pytest --cov=. --cov-report=term-missing
```

## 🔧 Configuración de Entorno

### Variables de Entorno (Opcional para Tests)
```bash
# Para tests de chat (opcional, se mockean)
export OPENAI_API_KEY="test-key"
export OPENAI_ASSISTANT_ID="test-assistant"

# Para tests de QR (opcional)
export FRONTEND_BASE_URL="http://localhost:5173"
```

### Base de Datos
Los tests usan SQLite en memoria, **no necesitas configurar PostgreSQL**.

## 📊 Interpretando Resultados

### Salida Exitosa
```
========================= test session starts =========================
collected 150 items

tests/test_main.py ......                                    [  4%]
tests/test_solicitudes.py ................................   [ 25%]
tests/test_qr.py ..........                                 [ 32%]
tests/test_admin.py .....................................    [ 56%]
tests/test_chat.py .............                           [ 65%]
tests/test_models.py ..........................              [ 82%]
tests/test_integration.py ........................          [100%]

========================= 150 passed in 45.2s =========================
```

### Salida con Errores
```
========================= FAILURES =========================
_____________ TestSolicitudesRouter.test_crear_solicitud _____________

    def test_crear_solicitud(self, client, sample_data):
        solicitud_data = {...}
>       response = client.post("/solicitudes", json=solicitud_data)
E       assert response.status_code == 200
E       AssertionError: assert 404 == 200

tests/test_solicitudes.py:123: AssertionError
========================= 1 failed, 149 passed in 42.1s =========================
```

## 🐛 Solución de Problemas Comunes

### Error: "Import pytest could not be resolved"
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Error: "No module named 'main'"
```bash
# Asegúrate de estar en el directorio correcto
cd TallerIntegracion-Back
```

### Error: Database errors
Los tests usan base de datos en memoria, si hay problemas:
```bash
# Limpiar caché de Python
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
```

### Tests lentos
```bash
# Ejecutar solo tests rápidos
pytest -m "not slow"

# Ejecutar en paralelo
pip install pytest-xdist
pytest -n auto
```

## 📈 Métricas y Cobertura

### Objetivo de Cobertura
- **Mínimo**: 80%
- **Objetivo**: 90%+
- **Excelente**: 95%+

### Verificar Cobertura
```bash
pytest --cov=. --cov-report=term-missing
```

### Reporte HTML
```bash
pytest --cov=. --cov-report=html
# Abrir: htmlcov/index.html
```

## 🔄 Integración Continua

### GitHub Actions (ejemplo)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: pytest --cov=. --cov-report=xml
```

## 📝 Escribir Nuevos Tests

### Estructura Básica
```python
import pytest

class TestNuevoEndpoint:
    def test_caso_exitoso(self, client, sample_data):
        response = client.get("/nuevo-endpoint")
        assert response.status_code == 200
        assert "expected_field" in response.json()
    
    def test_caso_error(self, client):
        response = client.get("/nuevo-endpoint/999")
        assert response.status_code == 404
```

### Usar Fixtures
```python
def test_con_datos(self, client, sample_data):
    # sample_data contiene todos los datos de prueba
    cama_id = sample_data["cama"].id_cama
    # ... resto del test
```

### Mockear Servicios Externos
```python
from unittest.mock import patch

@patch('services.external_service.call_api')
def test_con_mock(self, mock_api, client):
    mock_api.return_value = {"status": "ok"}
    # ... resto del test
```

## ✅ Checklist Pre-Deploy

Antes de hacer deploy, verifica:

- [ ] ✅ Todos los tests pasan
- [ ] ✅ Cobertura >= 80%
- [ ] ✅ No hay warnings importantes
- [ ] ✅ Tests de integración funcionan
- [ ] ✅ Mocks están actualizados
- [ ] ✅ Variables de entorno documentadas

---

**¿Necesitas ayuda?** Revisa los archivos de test existentes como ejemplos o consulta la documentación de pytest.