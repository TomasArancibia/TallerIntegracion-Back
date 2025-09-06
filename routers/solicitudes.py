from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter()

# Datos solicitud de los pacientes
class Solicitud(BaseModel):
    id: int
    cama_id: int
    area: str # Aseo, alimentación, mantención, etc
    descripcion: str
    fecha_solicitud: datetime
    estado: str = "pendiente"  # pendiente, en_proceso, completada
    fecha_cierre: Optional[datetime] = None

# Base de datos
solicitudes_db = []

# Crear una nueva solicitud
@router.post("/solicitudes")
def crear_solicitud(solicitud: Solicitud):
    solicitudes_db.append(solicitud)
    return {"mensaje": "Solicitud creada", "solicitud": solicitud}

# Obtener todas las solicitudes
@router.get("/solicitudes")
def obtener_solicitudes():
    return solicitudes_db
