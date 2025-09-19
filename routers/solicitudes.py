from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter()

#Modelos de datos

class Hospital(BaseModel):
    id_hospital: int
    nombre: str

class Habitacion(BaseModel):
    id_habitacion: int
    id_hospital: int
    numero: str

class Cama(BaseModel):
    id_cama: int
    id_habitacion: int
    identificador_qr: str

class Area(BaseModel):
    id_area: int
    nombre: str  # Ejemplo: Aseo, Alimentación, Mantención, Asistencia social

class Solicitud(BaseModel):
    id_solicitud: int
    id_cama: int
    id_area: int
    tipo: str # Aseo, alimentación, mantención, etc
    descripcion: str
    fecha_solicitud: datetime
    estado_actual: str = "pendiente"  # pendiente, en_proceso, completada
    fecha_creacion: datetime = datetime.now()
    fecha_en_proceso: Optional[datetime] = None
    fecha_resuelta: Optional[datetime] = None
    fecha_cancelada: Optional[datetime] = None

# Data en memoria

hospitales_db: List[Hospital] = [
    Hospital(id_hospital=1, nombre="UC Christus San Carlos de Apoquindo"),
    Hospital(id_hospital=2, nombre="UC Christus Casa Central")
]

habitaciones_db: List[Habitacion] = [
    Habitacion(id_habitacion=1, id_hospital=1, numero="101"),
    Habitacion(id_habitacion=2, id_hospital=1, numero="102"),
    Habitacion(id_habitacion=3, id_hospital=2, numero="201")
]

camas_db: List[Cama] = [
    Cama(id_cama=1, id_habitacion=1, identificador_qr="QR101A"),
    Cama(id_cama=2, id_habitacion=1, identificador_qr="QR101B"),
    Cama(id_cama=3, id_habitacion=2, identificador_qr="QR102A"),
    Cama(id_cama=4, id_habitacion=3, identificador_qr="QR201A")
]

areas_db: List[Area] = [
    Area(id_area=1, nombre="Aseo"),
    Area(id_area=2, nombre="Alimentación"),
    Area(id_area=3, nombre="Mantención"),
    Area(id_area=4, nombre="Asistencia social"),
    Area(id_area=5, nombre="Acompañamiento espiritual"),
]

# Base de datos
solicitudes_db = []

####################################################################################################
# SOLICITUDES

# Ver hospitales
@router.get("/hospitales")
def obtener_hospitales():
    return hospitales_db

# Ver habitaciones por hospital
@router.get("/hospitales/{id_hospital}/habitaciones")
def obtener_habitaciones_por_hospital(id_hospital: int):
    habitaciones = [hab for hab in habitaciones_db if hab.id_hospital == id_hospital]
    if not habitaciones:
        raise HTTPException(status_code=404, detail="No se encontraron habitaciones para este hospital")
    return habitaciones

# Ver camas por habitación
@router.get("/habitaciones/{id_habitacion}/camas")
def obtener_camas_por_habitacion(id_habitacion: int):
    camas = [cama for cama in camas_db if cama.id_habitacion == id_habitacion]
    if not camas:
        raise HTTPException(status_code=404, detail="No se encontraron camas para esta habitación")
    return camas

# Ver áreas
@router.get("/areas")
def obtener_areas():
    return areas_db

# Crear una nueva solicitud
@router.post("/solicitudes")
def crear_solicitud(solicitud: Solicitud):
    if not any(cama.id_cama == solicitud.id_cama for cama in camas_db):
        raise HTTPException(status_code=404, detail="Cama no encontrada")
    solicitudes_db.append(solicitud)

    if not any(area.id_area == solicitud.id_area for area in areas_db):
        raise HTTPException(status_code=404, detail="Área no encontrada")
    
    solicitudes_db.append(solicitud)
    return {"mensaje": "Solicitud creada", "solicitud": solicitud}

# Obtener todas las solicitudes
@router.get("/solicitudes")
def obtener_solicitudes():
    return solicitudes_db

# Solicitudes por cama
@router.get("/solicitudes/cama/{id_cama}")
def obtener_solicitudes_por_cama(id_cama: int):
    solicitudes = [sol for sol in solicitudes_db if sol.id_cama == id_cama]
    if not solicitudes:
        raise HTTPException(status_code=404, detail="No se encontraron solicitudes para esta cama")
    return solicitudes

# Actualizar estado de una solicitud
@router.put("/solicitudes/{id_solicitud}/estado")
def actualizar_estado_solicitud(id_solicitud: int, nuevo_estado: str):
    solicitud = next((sol for sol in solicitudes_db if sol.id_solicitud == id_solicitud), None)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    if nuevo_estado not in ["pendiente", "en_proceso", "completada", "cancelada"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    solicitud.estado_actual = nuevo_estado
    if nuevo_estado == "en_proceso":
        solicitud.fecha_en_proceso = datetime.now()
    elif nuevo_estado == "completada":
        solicitud.fecha_resuelta = datetime.now()
    elif nuevo_estado == "cancelada":
        solicitud.fecha_cancelada = datetime.now()
    
    return {"mensaje": "Estado actualizado", "solicitud": solicitud}
