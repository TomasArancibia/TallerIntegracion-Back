# TallerIntegracion-Back

Backend del proyecto de título (**FastAPI + PostgreSQL**).

![Backend Tests](https://github.com/TomasArancibia/TallerInt-Front/workflows/Backend%20Tests/badge.svg)
![Backend CI/CD](https://github.com/TomasArancibia/TallerInt-Front/workflows/Backend%20CI%2FCD/badge.svg)

---

## 🚀 Levantar entorno local

### 1. Activar entorno virtual (si no existe, crearlo)
```bash
python3 -m venv ~/.venvs/tallerint
source ~/.venvs/tallerint/bin/activate
```
```CMD
python -m venv ~/.venvs/tallerint
call "%USERPROFILE%\.venvs\tallerint\Scripts\activate.bat"
```

### 2. Instalar dependencias (solo la primera vez)
```pip install -r requirements.txt```

### 3 Ejecutar Backend
```uvicorn main:app --reload --port 8000```

La API quedará disponible en:
👉 http://127.0.0.1:8000

Documentación automática:
Swagger UI: http://127.0.0.1:8000/docs

## 🐳 Base de datos (Docker + PostgreSQL)
### 1. Levantar contenedores

Desde la raíz del backend:

```docker compose up -d```


Esto levanta Postgres en el puerto 5433 (internamente usa 5432) y pgAdmin en el puerto 5050.

### 2. Acceder a pgAdmin

👉 ```http://localhost:5050```

Credenciales de pgAdmin

```
Email: admin@uc.cl

Password: admin123
```

Servidor Postgres (ya configurado en docker-compose.yml)
```
Host: postgres (si lo accedes desde pgAdmin en Docker) o localhost (si lo accedes desde tu PC)

Port: 5433

Username: ucuser

Password: ucpass

Database: uchospital
```

### 3. 🛠 Migraciones con Alembic

Si hay cambios en los modelos de la base de datos:

Generar nueva migración:

```
alembic revision --autogenerate -m "descripcion_del_cambio"
```

Aplicar migraciones:

```
alembic upgrade head
```

### 4.🌱 Datos iniciales (seed)

Para poblar la DB con datos de ejemplo (hospital, habitaciones, camas, áreas, solicitudes):

python seed_full.py

## 📌 Endpoints principales

Hospitales
```
GET /hospitales → lista hospitales

GET /hospitales/{id} → obtener hospital por ID
```
Habitaciones
```
GET /hospitales/{id}/habitaciones → lista habitaciones de un hospital

GET /habitaciones/{id} → obtener habitación
```
Camas
```
GET /habitaciones/{id}/camas → lista camas de una habitación

GET /camas/{id} → obtener cama

GET /camas/by-qr/{qr} → buscar cama por QR
```
Áreas
```
GET /areas → lista áreas
```
Solicitudes
```
POST /solicitudes → crear solicitud

GET /solicitudes → listar solicitudes (con filtros por estado, hospital, habitación, cama)

GET /solicitudes/{id} → obtener solicitud por ID

PUT /solicitudes/{id}/estado → actualizar estado
```

## Para probar desde un qr válido desde el front:
```
http://localhost:5173/landing?qr=H1-201-1-A
```
Inválido:
```
http://localhost:5173/landing?qr=H1-101-B
```
## Para hacer login
```
http://localhost:5173/admin.html#/login
```

## 🚀 CI/CD y Testing Automático

### Tests Automáticos

Este proyecto tiene configurado **GitHub Actions** para ejecutar tests automáticamente:

- ✅ **En cada push** a cualquier branch
- ✅ **En cada Pull Request**
- ✅ **Antes de cada deploy** a producción

Los tests se ejecutan en **Python 3.11 y 3.12** para asegurar compatibilidad.

### Ejecutar Tests Localmente

```bash
# Ejecutar todos los tests
python -m pytest

# Ejecutar tests con más detalle
python -m pytest -v

# Ejecutar tests de un archivo específico
python -m pytest tests/test_endpoints_admin.py -v
```

### Validación Pre-Commit

Antes de hacer push, puedes ejecutar la validación completa:

**Windows:**
```cmd
scripts\pre-commit-check.bat
```

**Linux/Mac:**
```bash
./scripts/pre-commit-check.sh
```

### Verificar Conexión a Base de Datos

```bash
python db/test_connection.py
```

### Estado de CI/CD

Los badges en la parte superior del README muestran el estado actual de:
- 🧪 **Backend Tests**: Estado de los tests automáticos
- 🚀 **Backend CI/CD**: Estado del deploy automático

## URL BACKEND EN PRODUCCIÓN
```
https://tallerintegracion-back.onrender.com/
```

## URL FRONTEND EN PRODUCCIÓN
```
https://tallerint-front.vercel.app
```