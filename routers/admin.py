from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import secrets
import string
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.dependencies import require_admin, require_authenticated_user
from db.session import SessionLocal
from models.models import Area, Cama, Edificio, Habitacion, Institucion, Piso, RolUsuario, Servicio, Solicitud, Usuario
from pydantic import BaseModel, EmailStr
from routers.solicitudes import serialize_area, serialize_cama, serialize_edificio, serialize_habitacion, serialize_institucion, serialize_piso, serialize_servicio, serialize_solicitud
from services.supabase_admin import SupabaseAdminError, create_auth_user, delete_auth_user, update_auth_user


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
        "area_nombre": usuario.area.nombre_area if usuario.area else None,
        "activo": usuario.activo,
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
    # TZ
    try:
        tz_cl = ZoneInfo("America/Santiago")
    except Exception:
        tz_cl = timezone.utc

    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").replace(tzinfo=tz_cl)
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d").replace(tzinfo=tz_cl)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (YYYY-MM-DD)")

    if inicio > fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    inicio_utc = inicio.astimezone(timezone.utc)
    fin_utc_exclusive = (fin + timedelta(days=1)).astimezone(timezone.utc)

    solicitudes_filtro = db.query(Solicitud).filter(
        Solicitud.fecha_creacion >= inicio_utc,
        Solicitud.fecha_creacion < fin_utc_exclusive,
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
            func.date(func.timezone('America/Santiago', Solicitud.fecha_creacion)),
            func.count(Solicitud.id_solicitud),
        )
        .group_by(Area.nombre_area, func.date(func.timezone('America/Santiago', Solicitud.fecha_creacion)))
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


class UsuarioCreateRequest(BaseModel):
    email: EmailStr
    id_area: int


class ProfileUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    new_password: Optional[str] = None


class UsuarioAdminUpdateRequest(BaseModel):
    id_area: Optional[int] = None
    activo: Optional[bool] = None


@router.get("/users", summary="Listar jefes de área")
def admin_list_users(
    _: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    usuarios = (
        db.query(Usuario)
        .filter(Usuario.rol == RolUsuario.JEFE_AREA)
        .order_by(Usuario.correo)
        .all()
    )
    return {"usuarios": [serialize_usuario(u) for u in usuarios]}


def _generate_temp_password(email: str) -> str:
    suffix = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    prefix = email.split("@", 1)[0][:8] or "user"
    return f"{prefix}-{suffix}"


@router.post(
    "/users",
    summary="Crear jefe de área",
    status_code=status.HTTP_201_CREATED,
)
def admin_create_user(
    payload: UsuarioCreateRequest,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del admin  # unused, pero asegura que es admin

    area = db.query(Area).filter(Area.id_area == payload.id_area).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    existing = db.query(Usuario).filter(Usuario.correo == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")

    temp_password = _generate_temp_password(payload.email)

    try:
        supabase_response = create_auth_user(payload.email, temp_password)
    except SupabaseAdminError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user_data = supabase_response.get("user") or supabase_response
    user_id = user_data.get("id")
    if not user_id:
        raise HTTPException(
            status_code=500,
            detail="Supabase no devolvió un ID de usuario válido",
        )

    try:
        nuevo_usuario = Usuario(
            id=uuid.UUID(user_id),
            rol=RolUsuario.JEFE_AREA,
            correo=payload.email,
            nombre="Pendiente",
            apellido="Pendiente",
            telefono=None,
            id_area=area.id_area,
            activo=True,
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
    except Exception:
        db.rollback()
        # Si falló guardar en nuestra BD, intentamos revertir en Supabase
        try:
            delete_auth_user(user_id)
        except SupabaseAdminError:
            pass
        raise

    return {
        "usuario": serialize_usuario(nuevo_usuario),
        "temp_password": temp_password,
    }


@router.put("/me", summary="Actualizar perfil propio")
def admin_update_profile(
    payload: ProfileUpdateRequest,
    usuario: Usuario = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    usuario_db = db.query(Usuario).filter(Usuario.id == usuario.id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    updated = False

    if payload.nombre is not None:
        usuario_db.nombre = payload.nombre.strip() or usuario_db.nombre
        updated = True

    if payload.apellido is not None:
        usuario_db.apellido = payload.apellido.strip() or usuario_db.apellido
        updated = True

    if payload.telefono is not None:
        usuario_db.telefono = payload.telefono.strip() or None
        updated = True

    if updated:
        db.add(usuario_db)
        db.commit()
        db.refresh(usuario_db)

    if payload.new_password:
        try:
            update_auth_user(str(usuario.id), password=payload.new_password)
        except SupabaseAdminError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"usuario": serialize_usuario(usuario_db)}


@router.delete(
    "/users/{user_id}",
    summary="Eliminar jefe de área",
    status_code=status.HTTP_204_NO_CONTENT,
)
def admin_delete_user(
    user_id: str,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del admin  # solo para forzar autenticación

    try:
        uuid_user = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    usuario = db.query(Usuario).filter(Usuario.id == uuid_user).first()
    if not usuario:
        # Si no existe localmente, intentamos eliminar en Supabase igualmente
        try:
            delete_auth_user(user_id)
        except SupabaseAdminError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return

    if usuario.rol != RolUsuario.JEFE_AREA:
        raise HTTPException(status_code=400, detail="Solo se pueden eliminar usuarios de tipo JEFE_AREA")

    # Intentamos eliminar primero en Supabase
    try:
        delete_auth_user(user_id)
    except SupabaseAdminError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.delete(usuario)
    db.commit()

    return


@router.patch(
    "/users/{user_id}",
    summary="Actualizar jefe de área",
)
def admin_patch_user(
    user_id: str,
    payload: UsuarioAdminUpdateRequest,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del admin

    try:
        uuid_user = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    usuario = db.query(Usuario).filter(Usuario.id == uuid_user).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.rol != RolUsuario.JEFE_AREA:
        raise HTTPException(status_code=400, detail="Solo se pueden modificar usuarios de tipo JEFE_AREA")

    if payload.id_area is not None:
        area = db.query(Area).filter(Area.id_area == payload.id_area).first()
        if not area:
            raise HTTPException(status_code=404, detail="Área no encontrada")
        usuario.id_area = area.id_area

    if payload.activo is not None:
        usuario.activo = payload.activo

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return {"usuario": serialize_usuario(usuario)}


class HabitacionCreateRequest(BaseModel):
    nombre: str
    id_piso: int
    id_servicio: int


class CamaCreateRequest(BaseModel):
    id_habitacion: int
    letra: str
    identificador_qr: Optional[str] = None

class CamaUpdateRequest(BaseModel):
    activo: Optional[bool] = None


@router.post("/habitaciones", summary="Crear habitación", status_code=status.HTTP_201_CREATED)
def admin_crear_habitacion(
    payload: HabitacionCreateRequest,
    _: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    nombre = (payload.nombre or "").strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre de habitación requerido")

    piso = db.query(Piso).filter(Piso.id_piso == payload.id_piso).first()
    if not piso:
        raise HTTPException(status_code=404, detail="Piso no encontrado")

    servicio = db.query(Servicio).filter(Servicio.id_servicio == payload.id_servicio).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    existente = (
        db.query(Habitacion)
        .filter(Habitacion.id_piso == payload.id_piso, Habitacion.nombre_habitacion == nombre)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una habitación con ese nombre en el piso indicado")

    hab = Habitacion(nombre_habitacion=nombre, id_piso=piso.id_piso, id_servicio=servicio.id_servicio)
    db.add(hab)
    db.commit()
    db.refresh(hab)
    return {"habitacion": serialize_habitacion(hab)}


@router.post("/camas", summary="Crear cama", status_code=status.HTTP_201_CREATED)
def admin_crear_cama(
    payload: CamaCreateRequest,
    _: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    letra = (payload.letra or "").strip().upper()
    if not letra:
        raise HTTPException(status_code=400, detail="Letra de cama requerida")

    hab = db.query(Habitacion).filter(Habitacion.id_habitacion == payload.id_habitacion).first()
    if not hab:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    dup = (
        db.query(Cama)
        .filter(Cama.id_habitacion == payload.id_habitacion, Cama.letra_cama == letra)
        .first()
    )
    if dup:
        raise HTTPException(status_code=400, detail="Ya existe una cama con esa letra en la habitación")

    qr = (payload.identificador_qr or secrets.token_hex(16)).strip()

    # valida unicidad del QR
    if db.query(Cama).filter(Cama.identificador_qr == qr).first():
        # si vino desde el cliente, error; si fue generado, intenta regenerar unas veces
        if payload.identificador_qr:
            raise HTTPException(status_code=400, detail="El identificador QR ya existe")
        for _ in range(4):
            qr = secrets.token_hex(16)
            if not db.query(Cama).filter(Cama.identificador_qr == qr).first():
                break

    cama = Cama(id_habitacion=hab.id_habitacion, letra_cama=letra, identificador_qr=qr, activo=True)
    db.add(cama)
    db.commit()
    db.refresh(cama)
    return {"cama": serialize_cama(cama)}


@router.patch("/camas/{id_cama}", summary="Actualizar cama")
def admin_patch_cama(
    id_cama: int,
    payload: CamaUpdateRequest,
    _: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    cama = db.query(Cama).filter(Cama.id_cama == id_cama).first()
    if not cama:
        raise HTTPException(status_code=404, detail="Cama no encontrada")

    updated = False
    if payload.activo is not None:
        cama.activo = bool(payload.activo)
        updated = True

    if updated:
        db.add(cama)
        db.commit()
        db.refresh(cama)

    return {"cama": serialize_cama(cama)}
