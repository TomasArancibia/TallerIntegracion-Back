# seed_full.py
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from datetime import datetime, timedelta, UTC
from db.session import SessionLocal
from models.models import Hospital, Habitacion, Cama, Area, Solicitud, EstadoSolicitud

# ---------- helpers idempotentes ----------
def get_or_create(db: Session, model, defaults=None, **kwargs):
    inst = db.execute(select(model).filter_by(**kwargs)).scalar_one_or_none()
    if inst:
        return inst, False
    params = {**kwargs, **(defaults or {})}
    inst = model(**params)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst, True

def ensure_area(db: Session, nombre: str):
    return get_or_create(db, Area, nombre=nombre)[0]

def ensure_hospital(db: Session, nombre: str):
    return get_or_create(db, Hospital, nombre=nombre)[0]

def ensure_habitacion(db: Session, hospital: Hospital, numero: str):
    return get_or_create(db, Habitacion, id_hospital=hospital.id_hospital, numero=numero)[0]

def ensure_cama(db: Session, habitacion: Habitacion, identificador_qr: str, activo: bool = True):
    return get_or_create(
        db, Cama,
        identificador_qr=identificador_qr,
        defaults={"id_habitacion": habitacion.id_habitacion, "activo": activo}
    )[0]

def create_ticket(db: Session, cama: Cama, area: Area, tipo: str, descripcion: str,
                  estado: EstadoSolicitud, offset_days: int):
    """Crea ticket con fechas consistentes según estado y offset negativo (pasado)."""
    base = datetime.now(UTC) + timedelta(days=offset_days)

    # Fecha de cierre solo si estado requiere
    fecha_cierre = None
    if estado == EstadoSolicitud.RESUELTO:
        fecha_cierre = base + timedelta(hours=6)
    elif estado == EstadoSolicitud.CANCELADO:
        fecha_cierre = base + timedelta(hours=1)

    # fecha_actualizacion: siempre igual a base por defecto
    fecha_actualizacion = base

    s = Solicitud(
        id_cama=cama.id_cama,
        id_area=area.id_area,
        identificador_qr=cama.identificador_qr,
        tipo=tipo,
        descripcion=descripcion,
        estado_actual=estado,
        fecha_creacion=base,
        fecha_actualizacion=fecha_actualizacion,
        fecha_cierre=fecha_cierre
    )

    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# ---------- datos maestros ----------
AREAS = [
    "Mantención",
    "Nutrición y alimentación a pacientes",
    "Limpieza de habitación, baño o box",
    "Asistencia social",
    "Acompañamiento espiritual",
]
HAB_NUMS = ["101", "102", "103", "104"]
LETRAS = ["A", "B", "C"]  # 3 camas por habitación
TIPOS_MANT = [
    "BAÑO", "CLIMATIZACIÓN", "CAMA (LUCES, TIMBRE, ETC)", "TELEVISOR Y CONTROL REMOTO",
    "MOBILIARIO DENTRO DE LA HABITACIÓN", "OTRO TIPO DE MANTENCIÓN"
]


def clear_all_data(db: Session):
    """Elimina datos en orden correcto para evitar errores de FK"""
    db.execute(text("DELETE FROM solicitud"))
    db.execute(text("DELETE FROM cama"))
    db.execute(text("DELETE FROM habitacion"))
    db.execute(text("DELETE FROM hospital"))
    db.execute(text("DELETE FROM area"))
    db.commit()
    print("🧹 Tablas limpiadas correctamente.")



def seed_full():
    db = SessionLocal()
    try:

        clear_all_data(db)
        areas = {n: ensure_area(db, n) for n in AREAS}

        # 2) Hospitales y habitaciones
        h1 = ensure_hospital(db, "Hospital UC Christus Demo")
        h2 = ensure_hospital(db, "Clínica San Lucas")

        h1_habs = [ensure_habitacion(db, h1, n) for n in HAB_NUMS]
        h2_habs = [ensure_habitacion(db, h2, n) for n in HAB_NUMS]

        # 3) Camas (QR formateado: H<id_hospital>-<habitacion>-<letra>)
        def build_qr(hospital_id: int, numero: str, letra: str):
            return f"H{hospital_id}-{numero}-{letra}"

        camas_h1 = []
        for hab in h1_habs:
            for letra in LETRAS:
                qr = build_qr(h1.id_hospital, hab.numero, letra)
                activo = not (letra == "B" and hab.numero in ("101", "103"))
                camas_h1.append(ensure_cama(db, hab, qr, activo=activo))

        camas_h2 = []
        for hab in h2_habs:
            for letra in LETRAS:
                qr = build_qr(h2.id_hospital, hab.numero, letra)
                activo = not (letra == "C" and hab.numero in ("102", "104"))
                camas_h2.append(ensure_cama(db, hab, qr, activo=activo))

        # 4) Tickets de ejemplo distribuidos
        total_existentes = db.query(Solicitud).count()
        TARGET_TOTAL = 48  # sube si quieres más
        if total_existentes < TARGET_TOTAL:
            camas_all = camas_h1 + camas_h2

            estados = [
                EstadoSolicitud.PENDIENTE,
                EstadoSolicitud.EN_PROCESO,
                EstadoSolicitud.RESUELTO,
                EstadoSolicitud.CANCELADO,
            ]

            idx = 0
            for cama in camas_all:
                for _ in range(2):
                    estado = estados[idx % len(estados)]
                    tipo = TIPOS_MANT[idx % len(TIPOS_MANT)]
                    desc = f"{tipo} — ejemplo {idx+1}"
                    offset = -1 * ((idx % 14) + 1)
                    create_ticket(
                        db, cama, areas["Mantención"], tipo, desc, estado, offset
                    )
                    idx += 1

        print("✅ Seed FULL listo (idempotente).")
    finally:
        db.close()

if __name__ == "__main__":
    seed_full()
