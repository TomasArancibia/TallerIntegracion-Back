from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.dependencies import require_authenticated_user
from db.session import SessionLocal
from models.models import (
    Area,
    Cama,
    Edificio,
    Habitacion,
    Institucion,
    Piso,
    RolUsuario,
    Servicio,
    Solicitud,
    Usuario,
)
from routers.solicitudes import (
    serialize_area,
    serialize_cama,
    serialize_edificio,
    serialize_habitacion,
    serialize_institucion,
    serialize_piso,
    serialize_servicio,
    serialize_solicitud,
)


router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_usuario(usuario: Usuario) -> dict:
    return {
        "id": str(usuario.id),
        "rol": usuario.rol.value if hasattr(usuario.rol, "value") else usuario.rol,
        "correo": usuario.correo,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "telefono": usuario.telefono,
        "id_area": usuario.id_area,
    }


@router.get("/me", summary="Información del usuario autenticado")
def admin_me(usuario: Usuario = Depends(require_authenticated_user)):
    return {"usuario": serialize_usuario(usuario)}


@router.get("/bootstrap", summary="Datos base para el dashboard admin")
def admin_bootstrap(
    usuario: Usuario = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    instituciones = db.query(Institucion).order_by(Institucion.id_institucion).all()
    edificios = db.query(Edificio).order_by(Edificio.id_edificio).all()
    pisos = db.query(Piso).order_by(Piso.id_piso).all()
    servicios = db.query(Servicio).order_by(Servicio.id_servicio).all()
    areas = db.query(Area).order_by(Area.id_area).all()

    habitaciones = (
        db.query(Habitacion)
        .join(Piso)
        .join(Edificio)
        .order_by(Habitacion.id_habitacion)
        .all()
    )
    camas = db.query(Cama).order_by(Cama.id_cama).all()

    solicitudes_query = db.query(Solicitud).order_by(Solicitud.fecha_creacion.desc())
    if usuario.rol == RolUsuario.JEFE_AREA:
        if usuario.id_area is None:
            raise HTTPException(
                status_code=400,
                detail="El usuario jefe de área no tiene un área asignada",
            )
        solicitudes_query = solicitudes_query.filter(Solicitud.id_area == usuario.id_area)

    solicitudes = solicitudes_query.all()

    return {
        "usuario": serialize_usuario(usuario),
        "hospitales": [serialize_institucion(inst) for inst in instituciones],
        "edificios": [serialize_edificio(ed) for ed in edificios],
        "pisos": [serialize_piso(p) for p in pisos],
        "servicios": [serialize_servicio(s) for s in servicios],
        "habitaciones": [serialize_habitacion(h) for h in habitaciones],
        "camas": [serialize_cama(c) for c in camas],
        "areas": [serialize_area(a) for a in areas],
        "solicitudes": [serialize_solicitud(s) for s in solicitudes],
    }


@router.get("/metricas", summary="Métricas para dashboard admin")
def admin_metricas(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    usuario: Usuario = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (YYYY-MM-DD)")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    solicitudes_filtro = db.query(Solicitud).filter(
        Solicitud.fecha_creacion >= inicio,
        Solicitud.fecha_creacion <= fin,
    )

    if usuario.rol == RolUsuario.JEFE_AREA:
        if usuario.id_area is None:
            raise HTTPException(
                status_code=400,
                detail="El usuario jefe de área no tiene un área asignada",
            )
        solicitudes_filtro = solicitudes_filtro.filter(Solicitud.id_area == usuario.id_area)

    # Métrica por área
    metricas_area = (
        solicitudes_filtro.join(Area, Area.id_area == Solicitud.id_area)
        .with_entities(Area.nombre_area, func.count(Solicitud.id_solicitud))
        .group_by(Area.nombre_area)
        .all()
    )

    metricas_area_res = [
        {"nombre_area": nombre_area, "total_solicitudes": total}
        for nombre_area, total in metricas_area
    ]

    # Métrica por hospital y estado
    metricas_hospital_estado_query = (
        solicitudes_filtro.join(Cama, Cama.id_cama == Solicitud.id_cama)
        .join(Habitacion, Habitacion.id_habitacion == Cama.id_habitacion)
        .join(Piso, Piso.id_piso == Habitacion.id_piso)
        .join(Edificio, Edificio.id_edificio == Piso.id_edificio)
        .join(Institucion, Institucion.id_institucion == Edificio.id_institucion)
        .with_entities(
            Institucion.nombre_institucion,
            Solicitud.estado_actual,
            func.count(Solicitud.id_solicitud),
        )
        .group_by(Institucion.nombre_institucion, Solicitud.estado_actual)
        .all()
    )

    metricas_hospital_estado_res = [
        {
            "nombre_hospital": nombre_inst,
            "estado": estado.value if hasattr(estado, "value") else estado,
            "total_solicitudes": total,
        }
        for nombre_inst, estado, total in metricas_hospital_estado_query
    ]

    # Métrica por área y día
    metricas_area_dia_query = (
        solicitudes_filtro.join(Area, Area.id_area == Solicitud.id_area)
        .with_entities(
            Area.nombre_area,
            func.date(Solicitud.fecha_creacion),
            func.count(Solicitud.id_solicitud),
        )
        .group_by(Area.nombre_area, func.date(Solicitud.fecha_creacion))
        .all()
    )

    metricas_area_dia_res = [
        {
            "nombre_area": nombre_area,
            "dia": dia.isoformat() if hasattr(dia, "isoformat") else str(dia),
            "total_solicitudes": total,
        }
        for nombre_area, dia, total in metricas_area_dia_query
    ]

    return {
        "por_area": metricas_area_res,
        "por_hospital_estado": metricas_hospital_estado_res,
        "por_area_dia": metricas_area_dia_res,
    }
