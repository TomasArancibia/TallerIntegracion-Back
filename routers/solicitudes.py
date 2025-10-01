from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.models import Hospital, Habitacion, Cama, Area, Solicitud, EstadoSolicitud
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ======================
#   Pydantic Para recibir datos en formato JSON
# ======================

class SolicitudIn(BaseModel):
    id_cama: int                   # viene del QR (sessionStorage / validate)
    tipo: str                      # ej: "BAÑO", "CLIMATIZACIÓN", etc.
    descripcion: str               # texto libre del paciente
    id_area: Optional[int] = None  # opcional
    area_nombre: Optional[str] = None  # opcional (usaremos esto)

    class Config:
        extra = "ignore"  # ignora campos extra del front sin fallar

# ======================
#   DB DEPENDENCY
# ======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======================
#   HELPERS (serializers)
# ======================
def serialize_hospital(h: Hospital):
    return {"id_hospital": h.id_hospital, "nombre": h.nombre}

def serialize_habitacion(hab: Habitacion):
    return {"id_habitacion": hab.id_habitacion, "numero": hab.numero, "id_hospital": hab.id_hospital}

def serialize_cama(c: Cama):
    return {"id_cama": c.id_cama, "id_habitacion": c.id_habitacion, "qr": c.identificador_qr}

def serialize_area(a: Area):
    return {"id_area": a.id_area, "nombre": a.nombre}

def serialize_solicitud(s: Solicitud):
    return {
        "id": s.id_solicitud,
        "id_cama": s.id_cama,
        "id_area": s.id_area,
        "identificador_qr": s.identificador_qr,
        "tipo": s.tipo,
        "descripcion": s.descripcion,
        "estado": s.estado_actual,
        "fecha_creacion": s.fecha_creacion,
        "fecha_en_proceso": s.fecha_en_proceso,
        "fecha_resuelta": s.fecha_resuelta,
        "fecha_cancelada": s.fecha_cancelada,
    }


# ======================
#   HOSPITALES
# ======================
@router.get("/hospitales", summary="Listar hospitales")
def obtener_hospitales(db: Session = Depends(get_db)):
    hospitales = db.query(Hospital).all()
    return [serialize_hospital(h) for h in hospitales]

@router.get("/hospitales/{id_hospital}", summary="Obtener hospital por ID")
def obtener_hospital(id_hospital: int, db: Session = Depends(get_db)):
    h = db.query(Hospital).filter(Hospital.id_hospital == id_hospital).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")
    return serialize_hospital(h)


# ======================
#   HABITACIONES
# ======================
@router.get("/hospitales/{id_hospital}/habitaciones", summary="Listar habitaciones por hospital")
def obtener_habitaciones_por_hospital(id_hospital: int, db: Session = Depends(get_db)):
    # Verifica existencia del hospital para mensajes más claros
    if not db.query(Hospital).filter(Hospital.id_hospital == id_hospital).first():
        raise HTTPException(status_code=404, detail="Hospital no encontrado")

    habitaciones = db.query(Habitacion).filter(Habitacion.id_hospital == id_hospital).all()
    if not habitaciones:
        # Devolver lista vacía es válido; si prefieres 404, deja esta línea
        return []
    return [serialize_habitacion(h) for h in habitaciones]

@router.get("/habitaciones/{id_habitacion}", summary="Obtener habitación por ID")
def obtener_habitacion(id_habitacion: int, db: Session = Depends(get_db)):
    hab = db.query(Habitacion).filter(Habitacion.id_habitacion == id_habitacion).first()
    if not hab:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return serialize_habitacion(hab)


# ======================
#   CAMAS
# ======================
@router.get("/habitaciones/{id_habitacion}/camas", summary="Listar camas por habitación")
def obtener_camas_por_habitacion(id_habitacion: int, db: Session = Depends(get_db)):
    # Verifica existencia de la habitación
    if not db.query(Habitacion).filter(Habitacion.id_habitacion == id_habitacion).first():
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    camas = db.query(Cama).filter(Cama.id_habitacion == id_habitacion).all()
    return [serialize_cama(c) for c in camas]

@router.get("/camas/{id_cama}", summary="Obtener cama por ID")
def obtener_cama(id_cama: int, db: Session = Depends(get_db)):
    c = db.query(Cama).filter(Cama.id_cama == id_cama).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cama no encontrada")
    return serialize_cama(c)

@router.get("/camas/by-qr/{qr}", summary="Obtener cama por identificador QR")
def obtener_cama_por_qr(qr: str, db: Session = Depends(get_db)):
    c = db.query(Cama).filter(Cama.identificador_qr == qr).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cama no encontrada para ese QR")
    return serialize_cama(c)


# ======================
#   ÁREAS
# ======================
@router.get("/areas", summary="Listar áreas")
def obtener_areas(db: Session = Depends(get_db)):
    areas = db.query(Area).all()
    return [serialize_area(a) for a in areas]


# ======================
#   SOLICITUDES (tickets)
# ======================

@router.post("/solicitudes")
def crear_solicitud(payload: SolicitudIn, db: Session = Depends(get_db)):
    # Validar cama por id
    cama = db.query(Cama).filter(Cama.id_cama == payload.id_cama).first()
    if not cama:
        raise HTTPException(status_code=404, detail="Cama no encontrada")

    # Resolver área por id o por nombre (case-insensitive)
    area = None
    if payload.id_area:
        area = db.query(Area).filter(Area.id_area == payload.id_area).first()
    elif payload.area_nombre:
        area = db.query(Area).filter(Area.nombre.ilike(payload.area_nombre)).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    # Crear solicitud
    solicitud = Solicitud(
        id_cama=payload.id_cama,
        id_area=area.id_area,
        identificador_qr=cama.identificador_qr,
        tipo=payload.tipo,
        descripcion=payload.descripcion,
        estado_actual=EstadoSolicitud.ABIERTO,
        fecha_creacion=datetime.utcnow(),
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return {
        "mensaje": "Solicitud creada",
        "solicitud": {
            "id": solicitud.id_solicitud,
            "cama": solicitud.id_cama,
            "identificador_qr": solicitud.identificador_qr,
            "area": area.nombre,
            "estado": solicitud.estado_actual,
            "descripcion": solicitud.descripcion,
        },
    }


@router.get("/solicitudes", summary="Listar solicitudes con filtros")
def obtener_solicitudes(
    estado: str | None = Query(default=None, description="abierto | en_proceso | resuelto | cancelado"),
    id_hospital: int | None = Query(default=None),
    id_habitacion: int | None = Query(default=None),
    id_cama: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Filtros opcionales:
    - estado: 'abierto' | 'en_proceso' | 'resuelto' | 'cancelado'
    - id_hospital: filtra por hospital (via habitación->cama)
    - id_habitacion: filtra por habitación
    - id_cama: filtra por cama
    """
    q = db.query(Solicitud)

    if estado:
        if estado not in {"abierto", "en_proceso", "resuelto", "cancelado"}:
            raise HTTPException(status_code=400, detail="Estado inválido")
        q = q.filter(Solicitud.estado_actual == estado)

    if id_cama:
        q = q.filter(Solicitud.id_cama == id_cama)

    # Joins para filtrar por habitación/hospital
    if id_habitacion or id_hospital:
        q = q.join(Cama, Cama.id_cama == Solicitud.id_cama)
        if id_habitacion:
            q = q.filter(Cama.id_habitacion == id_habitacion)
        if id_hospital:
            q = q.join(Habitacion, Habitacion.id_habitacion == Cama.id_habitacion)
            q = q.filter(Habitacion.id_hospital == id_hospital)

    solicitudes = q.all()
    return [serialize_solicitud(s) for s in solicitudes]


@router.get("/solicitudes/{id_solicitud}", summary="Obtener solicitud por ID")
def obtener_solicitud(id_solicitud: int, db: Session = Depends(get_db)):
    s = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return serialize_solicitud(s)


@router.put("/solicitudes/{id_solicitud}/estado", summary="Actualizar estado de solicitud")
def actualizar_estado_solicitud(
    id_solicitud: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
):
    if nuevo_estado not in {"abierto", "en_proceso", "resuelto", "cancelado"}:
        raise HTTPException(status_code=400, detail="Estado inválido")

    s = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    s.estado_actual = nuevo_estado
    now = datetime.utcnow()
    if nuevo_estado == "en_proceso":
        s.fecha_en_proceso = now
    elif nuevo_estado == "resuelto":
        s.fecha_resuelta = now
    elif nuevo_estado == "cancelado":
        s.fecha_cancelada = now

    db.commit()
    db.refresh(s)
    return {"mensaje": "Estado actualizado", "solicitud": serialize_solicitud(s)}
