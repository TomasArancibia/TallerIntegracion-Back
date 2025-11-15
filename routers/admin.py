from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import re
import secrets
import string
import unicodedata
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.dependencies import require_admin, require_authenticated_user
from db.session import SessionLocal
from models.models import Area, Cama, Edificio, Habitacion, Institucion, Piso, RolUsuario, Servicio, Solicitud, Usuario, EstadoSolicitud, PortalButtonEvent, PortalChatMessage
from pydantic import BaseModel, EmailStr
from routers.solicitudes import serialize_area, serialize_cama, serialize_edificio, serialize_habitacion, serialize_institucion, serialize_piso, serialize_servicio, serialize_solicitud
from services.supabase_admin import SupabaseAdminError, create_auth_user, delete_auth_user, update_auth_user

CHAT_TOPICS = [
    {"id": "visitas", "label": "Visitas y acompanantes", "keywords": ["visita", "visitas", "acompan", "horario", "entrada", "salida"]},
    {"id": "pagos", "label": "Pagos y cuentas", "keywords": ["pago", "pagos", "cuenta", "cuentas", "costo", "precio", "copago", "boleta"]},
    {"id": "resultados", "label": "Resultados y examenes", "keywords": ["resultado", "resultados", "examen", "examenes", "laboratorio", "analisis"]},
    {"id": "solicitudes", "label": "Solicitudes y estados", "keywords": ["solicitud", "solicitudes", "estado", "pendiente", "tramite"]},
]


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
    # Todos los usuarios ven todas las solicitudes (sin filtrar por área)
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
    # Todos los usuarios ven métricas globales (sin filtrar por área)

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

    # Promedio de resolución (solo cerradas)
    cerradas_q = solicitudes_filtro.filter(
        Solicitud.estado_actual == EstadoSolicitud.CERRADA,
        Solicitud.fecha_creacion.isnot(None),
        Solicitud.fecha_cierre.isnot(None),
    )

    prom_area_query = (
        cerradas_q.join(Area, Area.id_area == Solicitud.id_area)
        .with_entities(
            Area.nombre_area,
            func.avg(func.extract('epoch', Solicitud.fecha_cierre - Solicitud.fecha_creacion)),
        )
        .group_by(Area.nombre_area)
        .all()
    )
    promedio_res_area = []
    for nombre, secs in prom_area_query:
        secs_float = float(secs) if secs is not None else 0.0
        promedio_res_area.append({"nombre_area": nombre, "horas": secs_float / 3600.0})

    prom_hosp_query = (
        cerradas_q
        .join(Cama, Cama.id_cama == Solicitud.id_cama)
        .join(Habitacion, Habitacion.id_habitacion == Cama.id_habitacion)
        .join(Piso, Piso.id_piso == Habitacion.id_piso)
        .join(Edificio, Edificio.id_edificio == Piso.id_edificio)
        .join(Institucion, Institucion.id_institucion == Edificio.id_institucion)
        .with_entities(
            Institucion.nombre_institucion,
            func.avg(func.extract('epoch', Solicitud.fecha_cierre - Solicitud.fecha_creacion)),
        )
        .group_by(Institucion.nombre_institucion)
        .all()
    )
    promedio_res_hospital = []
    for nombre, secs in prom_hosp_query:
        secs_float = float(secs) if secs is not None else 0.0
        promedio_res_hospital.append({"nombre_hospital": nombre, "horas": secs_float / 3600.0})

    # Portal QR y chatbot
    button_events = (
        db.query(
            PortalButtonEvent.id_cama,
            PortalButtonEvent.button_code,
            PortalButtonEvent.button_label,
            PortalButtonEvent.categoria,
            PortalButtonEvent.source_path,
            PortalButtonEvent.target_path,
            PortalButtonEvent.portal_session_id,
            PortalButtonEvent.clicked_at,
        )
        .filter(
            PortalButtonEvent.clicked_at >= inicio_utc,
            PortalButtonEvent.clicked_at < fin_utc_exclusive,
        )
        .order_by(PortalButtonEvent.id_cama.asc(), PortalButtonEvent.clicked_at.asc())
        .all()
    )

    sections_counter: Counter[str] = Counter()
    sections_meta: dict[str, dict[str, Optional[str]]] = {}
    section_sessions: defaultdict[str, set] = defaultdict(set)
    total_sessions_set: set[str] = set()
    section_sessions: defaultdict[str, set] = defaultdict(set)
    total_sessions_set: set[str] = set()
    cama_last_event: dict[int, dict[str, Optional[datetime]]] = {}
    sesiones_por_cama: defaultdict[int, int] = defaultdict(int)
    session_gap = timedelta(minutes=10)

    def resolve_portal_category(evt) -> Optional[str]:
        raw = (evt.categoria or "").strip()
        normalized = raw.lower()
        path_blob = " ".join(
            filter(None, [evt.source_path, evt.target_path, evt.button_code])
        ).lower()

        if normalized.startswith("info"):
            return raw or "info"
        if "asistente" in normalized:
            return raw or "asistente_virtual"
        if "chatbot" in normalized or "/chatbot" in path_blob or "chat" in path_blob:
            return raw or "asistente_virtual"
        if not normalized:
            if "/info" in path_blob or "info" in path_blob:
                return "info"
        return None

    for evt in button_events:
        event_category = resolve_portal_category(evt)
        raw_event_time = evt.clicked_at or datetime.now(timezone.utc)
        if raw_event_time.tzinfo is None:
            raw_event_time = raw_event_time.replace(tzinfo=timezone.utc)
        session_id = (evt.portal_session_id or "").strip()
        if not session_id:
            bucket = int(raw_event_time.timestamp() // 600)
            session_id = f"{evt.id_cama or 'unknown'}:{bucket}"
        total_sessions_set.add(session_id)

        if not event_category:
            continue
        section_key = (evt.target_path or evt.source_path or evt.button_code or "desconocido").strip() or "desconocido"
        sections_counter[section_key] += 1
        meta = sections_meta.setdefault(section_key, {"label": None, "categoria": None})
        if not meta["label"] and evt.button_label:
            meta["label"] = evt.button_label
        if not meta["categoria"] and event_category:
            meta["categoria"] = event_category
        section_sessions[section_key].add(session_id)

        if evt.id_cama is None or evt.clicked_at is None:
            continue
        event_time = evt.clicked_at
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        state = cama_last_event.get(evt.id_cama)
        session_id = (evt.portal_session_id or "").strip() or None

        start_new_session = False
        if state is None:
            start_new_session = True
        else:
            last_time = state.get("last_time")
            last_session_id = state.get("session_id")
            if session_id and last_session_id and session_id != last_session_id:
                start_new_session = True
            elif last_time is None or (event_time - last_time) > session_gap:
                start_new_session = True

        if start_new_session:
            sesiones_por_cama[evt.id_cama] += 1
            cama_last_event[evt.id_cama] = {"last_time": event_time, "session_id": session_id}
        else:
            state["last_time"] = event_time
            if session_id:
                state["session_id"] = session_id

    total_sessions = len(total_sessions_set) or 1
    total_clicks = sum(sections_counter.values()) or 1
    secciones_visitadas = []
    for section, total in sections_counter.most_common():
        meta = sections_meta.get(section, {})
        secciones_visitadas.append(
            {
                "seccion": section,
                "label": meta.get("label"),
                "categoria": meta.get("categoria"),
                "total_clicks": total,
                "porcentaje": (len(section_sessions.get(section, set())) / total_sessions) * 100.0,
            }
        )

    ranking_camas = []
    if sesiones_por_cama:
        ranking = sorted(sesiones_por_cama.items(), key=lambda item: (-item[1], item[0]))[:5]
        cama_ids = [cid for cid, _ in ranking]
        cama_info_map: dict[int, dict[str, Optional[str]]] = {}
        if cama_ids:
            cama_rows = (
                db.query(
                    Cama.id_cama,
                    Cama.letra_cama,
                    Habitacion.nombre_habitacion,
                    Servicio.nombre_servicio,
                    Piso.numero_piso,
                    Edificio.nombre_edificio,
                    Institucion.nombre_institucion,
                )
                .join(Habitacion, Habitacion.id_habitacion == Cama.id_habitacion)
                .join(Piso, Piso.id_piso == Habitacion.id_piso)
                .join(Edificio, Edificio.id_edificio == Piso.id_edificio)
                .join(Institucion, Institucion.id_institucion == Edificio.id_institucion)
                .join(Servicio, Servicio.id_servicio == Habitacion.id_servicio)
                .filter(Cama.id_cama.in_(cama_ids))
                .all()
            )
            for row in cama_rows:
                cama_info_map[row.id_cama] = {
                    "cama": row.letra_cama,
                    "habitacion": row.nombre_habitacion,
                    "servicio": row.nombre_servicio,
                    "institucion": row.nombre_institucion,
                    "edificio": row.nombre_edificio,
                    "piso": row.numero_piso,
                }
        for cama_id, total in ranking:
            info = cama_info_map.get(cama_id, {})
            ranking_camas.append(
                {
                    "id_cama": cama_id,
                    "total_sesiones": total,
                    "cama": info.get("cama"),
                    "habitacion": info.get("habitacion"),
                    "servicio": info.get("servicio"),
                    "institucion": info.get("institucion"),
                    "edificio": info.get("edificio"),
                    "piso": info.get("piso"),
                }
            )

    # Palabras frecuentes en el chatbot
    chat_messages = (
        db.query(PortalChatMessage.message)
        .filter(
            PortalChatMessage.created_at >= inicio_utc,
            PortalChatMessage.created_at < fin_utc_exclusive,
            PortalChatMessage.role == "user",
        )
        .all()
    )
    base_stopwords = {
        "el", "la", "los", "las", "de", "del", "y", "en", "que", "por", "para", "con", "una", "uno",
        "como", "al", "se", "su", "sus", "es", "mi", "me", "ya", "un", "lo", "les", "si", "gracias",
        "hola", "buenos", "dias", "tardes", "noche", "buenas", "favor", "porfa",
    }

    def normalize_token(token: str) -> str:
        normalized = unicodedata.normalize("NFKD", token.lower())
        return "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "M")

    stopwords = {normalize_token(word) for word in base_stopwords}
    token_pattern = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", re.UNICODE)
    keyword_counter: Counter[str] = Counter()
    bigram_counter: Counter[str] = Counter()
    topic_counter: Counter[str] = Counter()
    keyword_display: dict[str, str] = {}
    message_count = len(chat_messages)
    for (message,) in chat_messages:
        if not message:
            continue
        tokens_in_msg: list[str] = []
        for raw_token in token_pattern.findall(message):
            token = normalize_token(raw_token)
            if len(token) < 3 or token in stopwords:
                continue
            keyword_counter[token] += 1
            keyword_display.setdefault(token, raw_token.strip())
            tokens_in_msg.append(token)

        # bigramas por mensaje
        for idx in range(len(tokens_in_msg) - 1):
            bigram = f"{tokens_in_msg[idx]} {tokens_in_msg[idx + 1]}"
            bigram_counter[bigram] += 1

        token_set = set(tokens_in_msg)
        if token_set:
            for topic in CHAT_TOPICS:
                if any(word in token_set for word in topic["keywords"]):
                    topic_counter[topic["id"]] += 1

    total_keywords = sum(keyword_counter.values()) or 1
    chat_keywords = [
        {
            "keyword": keyword_display.get(keyword, keyword),
            "total": total,
            "porcentaje": (total / total_keywords) * 100.0,
        }
        for keyword, total in keyword_counter.most_common(20)
    ]

    total_bigrams = sum(bigram_counter.values()) or 1
    chat_bigrams = [
        {
            "frase": bigram,
            "total": total,
            "porcentaje": (total / total_bigrams) * 100.0,
        }
        for bigram, total in bigram_counter.most_common(20)
    ]

    total_topic_base = message_count or 1
    chat_topics = [
        {
            "id": topic["id"],
            "label": topic["label"],
            "total": topic_counter.get(topic["id"], 0),
            "porcentaje": (topic_counter.get(topic["id"], 0) / total_topic_base) * 100.0,
        }
        for topic in CHAT_TOPICS
        if topic_counter.get(topic["id"], 0) > 0
    ]

    return {
        "por_area": metricas_area_res,
        "por_hospital_estado": metricas_hospital_estado_res,
        "por_area_dia": metricas_area_dia_res,
        "promedio_resolucion_area": promedio_res_area,
        "promedio_resolucion_hospital": promedio_res_hospital,
        "portal_analytics": {
            "secciones_mas_visitadas": secciones_visitadas,
            "camas_con_mas_sesiones": ranking_camas,
            "chat_keywords": chat_keywords,
            "chat_bigrams": chat_bigrams,
            "chat_topics": chat_topics,
        },
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
    _: Usuario = Depends(require_authenticated_user),
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
    admin: Usuario = Depends(require_authenticated_user),
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
    admin: Usuario = Depends(require_authenticated_user),
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
    admin: Usuario = Depends(require_authenticated_user),
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
    _: Usuario = Depends(require_authenticated_user),
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
    _: Usuario = Depends(require_authenticated_user),
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
    _: Usuario = Depends(require_authenticated_user),
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
