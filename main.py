from fastapi import FastAPI
from routers import solicitudes
from routers import qr 
from routers import admin
from routers import analytics
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="UC Christus API - Gestión de Solicitudes",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_BASE_URL", "http://localhost:5173"),
    "http://localhost:5173",
    "https://ucchristusinformacionqr.netlify.app",
    "https://tallerint-front.vercel.app",
]

# Usamos la lista ALLOWED_ORIGINS para mayor claridad. Además añadimos una
# expresión regular que permita orígenes localhost con puerto y el dominio
# `ucchristusinformacionqr.netlify.app`. Nota: el Origin HTTP header nunca
# incluye la "ruta" (por ejemplo `/solicitudmantencion`), solo esquema+host+puerto,
# así que no hace falta listar subrutas.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Regex para cubrir localhost:<puerto> y el dominio netlify (por si hay
    # variaciones o subdominios dentro de Netlify).
    allow_origin_regex=r"^https?://(.+\.)?ucchristusinformacionqr\.netlify\.app(:\d+)?$|^http://localhost:\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(solicitudes.router)
app.include_router(qr.router)
app.include_router(admin.router)
app.include_router(analytics.router)
from routers.chat import router as chat_router
app.include_router(chat_router)

@app.get("/")
def correr_back():
    return {"mensaje": "Hola, mundo!. Cambio el back"}
