from fastapi import FastAPI
from routers import solicitudes
from routers import qr 
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="UC Christus API - Gestión de Solicitudes",
    version="1.0.0",
)

origins = [
    "https://ucchristusinformacionqr.netlify.app/", 
    "http://localhost",
    "http://127.0.0.1",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://localhost:\d+",  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(solicitudes.router)
app.include_router(qr.router)

@app.get("/")
def correr_back():
    return {"mensaje": "Hola, mundo!"}
