from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.models import (
    Area,
    Cama,
    Edificio,
    EstadoSolicitud,
    Habitacion,
    Institucion,
    Piso,
    Servicio,
    Solicitud,
)

router = APIRouter()


class SolicitudIn(BaseModel):
    id_cama: int
    tipo: str
    descripcion: Optional[str] = ""
    id_area: Optional[int] = None
    area_nombre: Optional[str] = None
    nombre_solicitante: Optional[str] = None
    correo_solicitante: Optional[str] = None

    class Config:
        extra = "ignore"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_institucion(inst: Institucion):
    return {"id_hospital": inst.id_institucion, "nombre": inst.nombre_institucion}


def serialize_edificio(edif: Edificio):
    return {
        "id_edificio": edif.id_edificio,
        "nombre": edif.nombre_edificio,
        "id_hospital": edif.id_institucion,
    }


def serialize_piso(p: Piso):
    return {
        "id_piso": p.id_piso,
        "numero": p.numero_piso,
        "id_edificio": p.id_edificio,
    }


def serialize_habitacion(hab: Habitacion):
    edf_id = hab.piso.edificio.id_institucion if hab.piso and hab.piso.edificio else None
    return {
        "id_habitacion": hab.id_habitacion,
        "nombre": hab.nombre_habitacion,
        "id_piso": hab.id_piso,
        "id_servicio": hab.id_servicio,
        "id_hospital": edf_id,
    }


def serialize_servicio(serv: Servicio):
    return {"id_servicio": serv.id_servicio, "nombre": serv.nombre_servicio}


def serialize_cama(c: Cama):
    return {
        "id_cama": c.id_cama,
        "id_habitacion": c.id_habitacion,
        "letra": c.letra_cama,
        "qr": c.identificador_qr,
        "activo": c.activo,
    }


def serialize_area(a: Area):
    return {"id_area": a.id_area, "nombre": a.nombre_area}


def serialize_solicitud(s: Solicitud):
    estado = s.estado_actual.value if hasattr(s.estado_actual, "value") else s.estado_actual
    cama = s.cama
    return {
        "id": s.id_solicitud,
        "id_cama": s.id_cama,
        "id_area": s.id_area,
        "tipo": s.tipo,
        "descripcion": s.descripcion,
        "estado": estado,
        "fecha_creacion": s.fecha_creacion.isoformat() if s.fecha_creacion else None,
        "fecha_actualizacion": s.fecha_actualizacion.isoformat() if s.fecha_actualizacion else None,
        "fecha_cierre": s.fecha_cierre.isoformat() if s.fecha_cierre else None,
        "nombre_solicitante": s.nombre_solicitante,
        "correo_solicitante": s.correo_solicitante,
        "identificador_qr": cama.identificador_qr if cama else None,
    }


def resolve_estado(value: str) -> EstadoSolicitud:
    if not value:
        raise HTTPException(status_code=400, detail="Estado no puede ser vacío")

    normalized = value.strip().lower().replace(" ", "_")
    for miembro in EstadoSolicitud:
        if normalized == miembro.value:
            return miembro

    raise HTTPException(
        status_code=400,
        detail=f"Estado inválido. Valores permitidos: {[e.value for e in EstadoSolicitud]}",
    )


@router.get("/hospitales", summary="Listar instituciones (alias hospitales)")
def obtener_hospitales(db: Session = Depends(get_db)):
    instituciones = db.query(Institucion).order_by(Institucion.id_institucion).all()
    return [serialize_institucion(inst) for inst in instituciones]


@router.get("/hospitales/{id_hospital}", summary="Obtener institución por ID")
def obtener_hospital(id_hospital: int, db: Session = Depends(get_db)):
    inst = db.query(Institucion).filter(Institucion.id_institucion == id_hospital).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return serialize_institucion(inst)


@router.get("/edificios", summary="Listar edificios")
def obtener_edificios(db: Session = Depends(get_db)):
    edificios = db.query(Edificio).order_by(Edificio.id_edificio).all()
    return [serialize_edificio(e) for e in edificios]


@router.get("/hospitales/{id_hospital}/edificios", summary="Listar edificios por institución")
def obtener_edificios_por_hospital(id_hospital: int, db: Session = Depends(get_db)):
    if not db.query(Institucion).filter(Institucion.id_institucion == id_hospital).first():
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    edificios = db.query(Edificio).filter(Edificio.id_institucion == id_hospital).all()
    return [serialize_edificio(e) for e in edificios]


@router.get("/pisos", summary="Listar pisos")
def obtener_pisos(db: Session = Depends(get_db)):
    pisos = db.query(Piso).order_by(Piso.id_piso).all()
    return [serialize_piso(p) for p in pisos]


@router.get("/edificios/{id_edificio}/pisos", summary="Listar pisos por edificio")
def obtener_pisos_por_edificio(id_edificio: int, db: Session = Depends(get_db)):
    if not db.query(Edificio).filter(Edificio.id_edificio == id_edificio).first():
        raise HTTPException(status_code=404, detail="Edificio no encontrado")
    pisos = db.query(Piso).filter(Piso.id_edificio == id_edificio).all()
    return [serialize_piso(p) for p in pisos]


@router.get("/servicios", summary="Listar servicios clínicos")
def obtener_servicios(db: Session = Depends(get_db)):
    servicios = db.query(Servicio).order_by(Servicio.id_servicio).all()
    return [serialize_servicio(s) for s in servicios]


@router.get("/habitaciones", summary="Listar habitaciones")
def obtener_habitaciones(db: Session = Depends(get_db)):
    habitaciones = db.query(Habitacion).join(Piso).join(Edificio).all()
    return [serialize_habitacion(h) for h in habitaciones]


@router.get("/hospitales/{id_hospital}/habitaciones", summary="Listar habitaciones por hospital")
def obtener_habitaciones_por_hospital(id_hospital: int, db: Session = Depends(get_db)):
    if not db.query(Institucion).filter(Institucion.id_institucion == id_hospital).first():
        raise HTTPException(status_code=404, detail="Institución no encontrada")

    habitaciones = (
        db.query(Habitacion)
        .join(Piso)
        .join(Edificio)
        .filter(Edificio.id_institucion == id_hospital)
        .all()
    )
    return [serialize_habitacion(h) for h in habitaciones]


@router.get("/habitaciones/{id_habitacion}", summary="Obtener habitación por ID")
def obtener_habitacion(id_habitacion: int, db: Session = Depends(get_db)):
    hab = (
        db.query(Habitacion)
        .filter(Habitacion.id_habitacion == id_habitacion)
        .first()
    )
    if not hab:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return serialize_habitacion(hab)


@router.get("/camas", summary="Listar camas")
def obtener_camas(db: Session = Depends(get_db)):
    camas = db.query(Cama).order_by(Cama.id_cama).all()
    return [serialize_cama(c) for c in camas]


@router.get("/habitaciones/{id_habitacion}/camas", summary="Listar camas por habitación")
def obtener_camas_por_habitacion(id_habitacion: int, db: Session = Depends(get_db)):
    if not db.query(Habitacion).filter(Habitacion.id_habitacion == id_habitacion).first():
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    camas = db.query(Cama).filter(Cama.id_habitacion == id_habitacion).all()
    return [serialize_cama(c) for c in camas]


@router.get("/camas/{id_cama}", summary="Obtener cama por ID")
def obtener_cama(id_cama: int, db: Session = Depends(get_db)):
    cama = db.query(Cama).filter(Cama.id_cama == id_cama).first()
    if not cama:
        raise HTTPException(status_code=404, detail="Cama no encontrada")
    return serialize_cama(cama)


@router.get("/camas/by-qr/{qr}", summary="Obtener cama por identificador QR")
def obtener_cama_por_qr(qr: str, db: Session = Depends(get_db)):
    cama = db.query(Cama).filter(Cama.identificador_qr == qr).first()
    if not cama:
        raise HTTPException(status_code=404, detail="Cama no encontrada para ese QR")
    return serialize_cama(cama)


@router.get("/areas", summary="Listar áreas")
def obtener_areas(db: Session = Depends(get_db)):
    areas = db.query(Area).order_by(Area.id_area).all()
    return [serialize_area(a) for a in areas]


@router.post("/solicitudes", summary="Crear solicitud")
def crear_solicitud(payload: SolicitudIn, db: Session = Depends(get_db)):
    cama = db.query(Cama).filter(Cama.id_cama == payload.id_cama).first()
    if not cama:
        raise HTTPException(status_code=404, detail="Cama no encontrada")

    area: Optional[Area] = None
    if payload.id_area is not None:
        area = db.query(Area).filter(Area.id_area == payload.id_area).first()
    elif payload.area_nombre:
        area = (
            db.query(Area)
            .filter(func.lower(Area.nombre_area) == payload.area_nombre.strip().lower())
            .first()
        )

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    tipo = (payload.tipo or "").strip()
    if not tipo:
        raise HTTPException(status_code=400, detail="Tipo de solicitud requerido")
    now = datetime.now(timezone.utc)

    solicitud = Solicitud(
        id_cama=cama.id_cama,
        id_area=area.id_area,
        tipo=tipo,
        descripcion=(payload.descripcion or "").strip(),
        estado_actual=EstadoSolicitud.PENDIENTE,
        fecha_creacion=now,
        fecha_actualizacion=now,
        nombre_solicitante=payload.nombre_solicitante,
        correo_solicitante=payload.correo_solicitante,
    )

    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return {"mensaje": "Solicitud creada", "solicitud": serialize_solicitud(solicitud)}


@router.get("/solicitudes", summary="Listar solicitudes con filtros")
def obtener_solicitudes(
    estado: Optional[str] = Query(default=None, description="pendiente | en_proceso | cerrada"),
    id_hospital: Optional[int] = Query(default=None),
    id_habitacion: Optional[int] = Query(default=None),
    id_cama: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(Solicitud)

    if estado:
        estado_enum = resolve_estado(estado)
        q = q.filter(Solicitud.estado_actual == estado_enum)

    if id_cama:
        q = q.filter(Solicitud.id_cama == id_cama)

    if id_habitacion or id_hospital:
        q = q.join(Cama, Cama.id_cama == Solicitud.id_cama).join(Habitacion, Habitacion.id_habitacion == Cama.id_habitacion)
        if id_habitacion:
            q = q.filter(Habitacion.id_habitacion == id_habitacion)
        if id_hospital:
            q = (
                q.join(Piso, Piso.id_piso == Habitacion.id_piso)
                .join(Edificio, Edificio.id_edificio == Piso.id_edificio)
                .filter(Edificio.id_institucion == id_hospital)
            )

    solicitudes = q.order_by(Solicitud.fecha_creacion.desc()).all()
    return [serialize_solicitud(s) for s in solicitudes]


@router.get("/solicitudes/{id_solicitud}", summary="Obtener solicitud por ID")
def obtener_solicitud(id_solicitud: int, db: Session = Depends(get_db)):
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return serialize_solicitud(solicitud)


@router.put("/solicitudes/{id_solicitud}/estado", summary="Actualizar estado de solicitud")
def actualizar_estado_solicitud(
    id_solicitud: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
):
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    estado_enum = resolve_estado(nuevo_estado)
    now = datetime.now(timezone.utc)

    if solicitud.estado_actual != estado_enum:
        solicitud.estado_actual = estado_enum
        solicitud.fecha_actualizacion = now
        if estado_enum == EstadoSolicitud.CERRADA:
            solicitud.fecha_cierre = now
        else:
            solicitud.fecha_cierre = None
        db.commit()
        db.refresh(solicitud)

    return {"mensaje": "Estado actualizado", "solicitud": serialize_solicitud(solicitud)}


@router.get("/metricas/solicitudes-por-fecha", summary="Solicitudes creadas en rango de fechas")
def metricas_solicitudes_por_fecha(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    count = (
        db.query(func.count(Solicitud.id_solicitud))
        .filter(Solicitud.fecha_creacion >= inicio, Solicitud.fecha_creacion <= fin)
        .scalar()
    )

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "total_solicitudes": count or 0}


@router.get("/metricas/solicitudes-por-area", summary="Solicitudes por área en rango de fechas")
def metricas_solicitudes_por_area(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    resultados = (
        db.query(
            Area.nombre_area,
            func.count(Solicitud.id_solicitud),
        )
        .join(Solicitud, Solicitud.id_area == Area.id_area)
        .filter(Solicitud.fecha_creacion >= inicio, Solicitud.fecha_creacion <= fin)
        .group_by(Area.nombre_area)
        .all()
    )

    metricas = [
        {"nombre_area": nombre_area, "total_solicitudes": total}
        for nombre_area, total in resultados
    ]

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "metricas": metricas}


@router.get(
    "/metricas/solicitudes-por-hospital-estado",
    summary="Solicitudes por hospital e estado en rango de fechas",
)
def metricas_solicitudes_por_hospital_estado(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    resultados = (
        db.query(
            Institucion.nombre_institucion,
            Solicitud.estado_actual,
            func.count(Solicitud.id_solicitud),
        )
        .join(Edificio, Edificio.id_institucion == Institucion.id_institucion)
        .join(Piso, Piso.id_edificio == Edificio.id_edificio)
        .join(Habitacion, Habitacion.id_piso == Piso.id_piso)
        .join(Cama, Cama.id_habitacion == Habitacion.id_habitacion)
        .join(Solicitud, Solicitud.id_cama == Cama.id_cama)
        .filter(Solicitud.fecha_creacion >= inicio, Solicitud.fecha_creacion <= fin)
        .group_by(Institucion.nombre_institucion, Solicitud.estado_actual)
        .all()
    )

    metricas = [
        {
            "nombre_hospital": nombre_inst,
            "estado": estado.value if hasattr(estado, "value") else estado,
            "total_solicitudes": total,
        }
        for nombre_inst, estado, total in resultados
    ]

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "metricas": metricas}


@router.get(
    "/metricas/solicitudes-por-hospital-area",
    summary="Solicitudes por hospital y área en rango de fechas",
)
def metricas_solicitudes_por_hospital_area(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    resultados = (
        db.query(
            Institucion.nombre_institucion,
            Area.nombre_area,
            func.count(Solicitud.id_solicitud),
        )
        .join(Edificio, Edificio.id_institucion == Institucion.id_institucion)
        .join(Piso, Piso.id_edificio == Edificio.id_edificio)
        .join(Habitacion, Habitacion.id_piso == Piso.id_piso)
        .join(Cama, Cama.id_habitacion == Habitacion.id_habitacion)
        .join(Solicitud, Solicitud.id_cama == Cama.id_cama)
        .join(Area, Area.id_area == Solicitud.id_area)
        .filter(Solicitud.fecha_creacion >= inicio, Solicitud.fecha_creacion <= fin)
        .group_by(Institucion.nombre_institucion, Area.nombre_area)
        .all()
    )

    metricas = [
        {
            "nombre_hospital": nombre_inst,
            "nombre_area": nombre_area,
            "total_solicitudes": total,
        }
        for nombre_inst, nombre_area, total in resultados
    ]

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "metricas": metricas}


@router.get(
    "/metricas/solicitudes-por-area-dia",
    summary="Solicitudes por área por día en rango de fechas",
)
def metricas_solicitudes_por_area_dia(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    resultados = (
        db.query(
            Area.nombre_area,
            func.date(Solicitud.fecha_creacion),
            func.count(Solicitud.id_solicitud),
        )
        .join(Solicitud, Solicitud.id_area == Area.id_area)
        .filter(Solicitud.fecha_creacion >= inicio, Solicitud.fecha_creacion <= fin)
        .group_by(Area.nombre_area, func.date(Solicitud.fecha_creacion))
        .all()
    )

    metricas = [
        {
            "nombre_area": nombre_area,
            "dia": dia.isoformat() if hasattr(dia, "isoformat") else str(dia),
            "total_solicitudes": total,
        }
        for nombre_area, dia, total in resultados
    ]

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "metricas": metricas}


@router.get(
    "/metricas/tiempo-promedio-resolucion",
    summary="Tiempo promedio de resolución de solicitudes (horas)",
)
def metricas_tiempo_promedio_resolucion(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    promedio_segundos = (
        db.query(
            func.avg(
                func.extract("epoch", (Solicitud.fecha_cierre - Solicitud.fecha_creacion))
            )
        )
        .filter(
            Solicitud.fecha_creacion >= inicio,
            Solicitud.fecha_creacion <= fin,
            Solicitud.estado_actual == EstadoSolicitud.CERRADA,
        )
        .scalar()
    )

    promedio_horas = (promedio_segundos or 0) / 3600

    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "tiempo_promedio_resolucion_horas": round(promedio_horas, 2),
    }


@router.get(
    "/metricas/tiempo-promedio-resolucion-por-area",
    summary="Tiempo promedio de resolución por área (horas)",
)
def metricas_tiempo_promedio_resolucion_por_area(
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    resultados = (
        db.query(
            Area.nombre_area,
            func.avg(
                func.extract("epoch", (Solicitud.fecha_cierre - Solicitud.fecha_creacion))
            ),
        )
        .join(Solicitud, Solicitud.id_area == Area.id_area)
        .filter(
            Solicitud.fecha_creacion >= inicio,
            Solicitud.fecha_creacion <= fin,
            Solicitud.estado_actual == EstadoSolicitud.CERRADA,
        )
        .group_by(Area.nombre_area)
        .all()
    )

    metricas = [
        {
            "nombre_area": nombre_area,
            "tiempo_promedio_resolucion_horas": round(((promedio or 0) / 3600), 2),
        }
        for nombre_area, promedio in resultados
    ]

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "metricas": metricas}
