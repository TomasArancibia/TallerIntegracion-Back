from fastapi import FastAPI
from routers import solicitudes
from routers import qr 
from routers import admin
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="UC Christus API - Gestión de Solicitudes",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_BASE_URL", "http://localhost:5173"),
    "http://localhost:5173",
    "https://ucchristusinformacionqr.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ucchristusinformacionqr.netlify.app",  
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(solicitudes.router)
app.include_router(qr.router)
app.include_router(admin.router)

@app.get("/")
def correr_back():
    return {"mensaje": "Hola, mundo!. Cambio el back"}
