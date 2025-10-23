# TallerIntegracion-Back

Backend del proyecto de título (**FastAPI + PostgreSQL**).

---

## 🚀 Levantar entorno local

### 1. Activar entorno virtual (si no existe, crearlo)
```bash
python3 -m venv ~/.venvs/tallerint
source ~/.venvs/tallerint/bin/activate
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
http://localhost:5173/landing?qr=H1-101-A
```
Inválido:
```
http://localhost:5173/landing?qr=H1-101-B
```
