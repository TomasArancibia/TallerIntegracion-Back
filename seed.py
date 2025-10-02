from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from models.models import Hospital, Habitacion, Cama, Area, Solicitud, EstadoSolicitud
from datetime import datetime

# Función para limpiar e insertar datos
def seed_data(db: Session):
    # Borrar datos previos (opcional, útil en desarrollo)
    db.query(Solicitud).delete()
    db.query(Cama).delete()
    db.query(Habitacion).delete()
    db.query(Hospital).delete()
    db.query(Area).delete()
    db.commit()

    # Crear hospital demo
    hospital = Hospital(nombre="Hospital UC Christus Demo")
    db.add(hospital)
    db.commit()
    db.refresh(hospital)

    # Crear habitaciones
    habitacion1 = Habitacion(numero="101", hospital=hospital)
    habitacion2 = Habitacion(numero="102", hospital=hospital)
    db.add_all([habitacion1, habitacion2])
    db.commit()
    db.refresh(habitacion1)
    db.refresh(habitacion2)

    # Crear camas con QR
    cama_101A = Cama(identificador_qr="H1-101-A", habitacion=habitacion1, activo=True)
    cama_101B = Cama(identificador_qr="H1-101-B", habitacion=habitacion1, activo=False)  # inactiva para pruebas
    cama_102A = Cama(identificador_qr="H1-102-A", habitacion=habitacion2, activo=True)
    db.add_all([cama_101A, cama_101B, cama_102A]); db.commit()

    # Crear áreas
    area1 = Area(nombre="Mantención")
    area2 = Area(nombre="Aseo")
    area3 = Area(nombre="Alimentación")
    db.add_all([area1, area2, area3])
    db.commit()
    db.refresh(area1)

    # Crear solicitud de ejemplo
    solicitud = Solicitud(
        cama=cama_101A,
        area=area1,
        tipo="Reparación",
        descripcion="La luz de la habitación no funciona",
        estado_actual=EstadoSolicitud.ABIERTO,
        fecha_creacion=datetime.utcnow(),
    )
    db.add(solicitud)
    db.commit()

    print("✅ Datos iniciales insertados con éxito")

# Script principal
if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
