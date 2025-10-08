from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Cargar variables desde .env (aunque en Render se inyectan directo)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Crear motor de conexión
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # evita usar conexiones muertas
    pool_size=3,          # límites modestos para free tier
    max_overflow=0,
)

# Sesión local para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para definir modelos (tablas)
Base = declarative_base()
