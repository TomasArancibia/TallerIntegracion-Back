# Tests del Backend - TallerIntegracion

Esta carpeta contiene la suite completa de tests para todos los endpoints y funcionalidades del backend.

## Estructura de Tests

```
tests/
├── conftest.py              # Configuración común y fixtures
├── test_main.py            # Tests para endpoints principales
├── test_solicitudes.py     # Tests para router de solicitudes
├── test_qr.py              # Tests para router de QR
├── test_admin.py           # Tests para router de administración
├── test_chat.py            # Tests para router de chat
├── test_models.py          # Tests para validación de modelos
├── test_integration.py     # Tests de integración
└── README.md               # Este archivo
```

## Cobertura de Tests

### 🏥 Router de Solicitudes (`test_solicitudes.py`)
- ✅ CRUD completo de solicitudes
- ✅ Gestión de hospitales, edificios, pisos, habitaciones
- ✅ Gestión de servicios, áreas y camas
- ✅ Filtros y búsquedas
- ✅ Cambios de estado de solicitudes
- ✅ Métricas y reportes
- ✅ Validaciones y manejo de errores

### 🔍 Router de QR (`test_qr.py`)
- ✅ Validación de códigos QR
- ✅ Generación de imágenes QR
- ✅ Generación de lotes de QR (ZIP)
- ✅ Redirecciones
- ✅ Manejo de QR inactivos e inexistentes

### 👨‍💼 Router de Administración (`test_admin.py`)
- ✅ Autenticación y autorización
- ✅ Gestión de usuarios (CRUD)
- ✅ Dashboard y métricas administrativas
- ✅ Creación de habitaciones y camas
- ✅ Actualización de perfiles
- ✅ Integración con Supabase

### 💬 Router de Chat (`test_chat.py`)
- ✅ Chat con asistente de OpenAI
- ✅ Chat completions
- ✅ Manejo de errores de API externa
- ✅ Timeouts y respuestas vacías
- ✅ Configuración de variables de entorno

### 🗄️ Modelos de Datos (`test_models.py`)
- ✅ Validación de todos los modelos
- ✅ Constraints y validaciones de BD
- ✅ Relaciones entre entidades
- ✅ Enums y valores por defecto
- ✅ Campos nullable y requeridos

### 🔗 Tests de Integración (`test_integration.py`)
- ✅ Flujos completos end-to-end
- ✅ Interacción entre múltiples endpoints
- ✅ Validación de jerarquías de datos
- ✅ Transiciones de estados
- ✅ Filtros complejos

### 🏠 Aplicación Principal (`test_main.py`)
- ✅ Endpoint raíz
- ✅ CORS y headers
- ✅ Manejo de errores HTTP

## Tecnologías Utilizadas

- **pytest**: Framework principal de testing
- **FastAPI TestClient**: Cliente de pruebas para FastAPI
- **SQLAlchemy**: Base de datos en memoria para tests
- **SQLite**: Base de datos de pruebas
- **unittest.mock**: Mocking para servicios externos

## Instalación y Configuración

1. **Instalar dependencias de testing:**
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

2. **Ejecutar todos los tests:**
```bash
pytest
```

3. **Ejecutar tests con cobertura:**
```bash
pytest --cov=. --cov-report=html
```

4. **Ejecutar tests específicos:**
```bash
# Solo tests de solicitudes
pytest tests/test_solicitudes.py

# Solo tests de QR
pytest tests/test_qr.py

# Solo tests de admin
pytest tests/test_admin.py
```

5. **Ejecutar tests con verbose:**
```bash
pytest -v
```

## Configuración de Base de Datos

Los tests utilizan una base de datos SQLite en memoria que se crea y destruye para cada test, garantizando:
- ✅ Aislamiento completo entre tests
- ✅ Velocidad de ejecución
- ✅ Sin dependencias externas
- ✅ Datos de prueba consistentes

## Mocking de Servicios Externos

Los tests incluyen mocks para:
- 🔐 Autenticación de Supabase
- 🤖 API de OpenAI
- 📧 Envío de emails
- 🌐 Variables de entorno

## Fixtures Disponibles

### `db_session`
Proporciona una sesión de base de datos limpia para cada test.

### `client`
Cliente de pruebas de FastAPI configurado.

### `sample_data`
Datos de prueba completos incluyendo:
- Hospital, edificio, piso
- Servicio, área, habitación, cama
- Usuarios admin y jefe de área
- Solicitud de ejemplo

### `auth_headers`
Headers de autenticación mock para endpoints protegidos.

## Resultados Esperados

Al ejecutar la suite completa de tests, deberías ver:
- ✅ **200+ tests** ejecutados exitosamente
- ✅ Cobertura de código **>90%**
- ✅ Todos los endpoints validados
- ✅ Todos los flujos de negocio probados
- ✅ Manejo de errores verificado

## Casos de Prueba Incluidos

### ✅ Happy Path (Casos Exitosos)
- Operaciones CRUD normales
- Flujos de usuario típicos
- Respuestas correctas de API

### ❌ Error Handling (Manejo de Errores)
- Recursos no encontrados (404)
- Datos inválidos (422)
- Restricciones de BD (400)
- Errores de autenticación (401/403)
- Errores de servicios externos (500)

### 🔍 Edge Cases (Casos Límite)
- Datos vacíos o nulos
- Valores extremos
- Concurrencia y race conditions
- Timeouts y reintentos

## Mantenimiento

Para mantener los tests actualizados:

1. **Agregar tests para nuevos endpoints**
2. **Actualizar fixtures cuando cambien los modelos**
3. **Mantener mocks actualizados con APIs externas**
4. **Revisar cobertura regularmente**
5. **Documentar casos de prueba especiales**

## Ejecución en CI/CD

Los tests están diseñados para ejecutarse en pipelines de CI/CD:
- ✅ Sin dependencias externas
- ✅ Ejecución determinística
- ✅ Salida compatible con herramientas de CI
- ✅ Reportes de cobertura exportables

---

**Nota**: Esta suite de tests cubre todos los endpoints y funcionalidades del backend, proporcionando una base sólida para el desarrollo y mantenimiento del sistema.