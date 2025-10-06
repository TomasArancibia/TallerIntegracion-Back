# db/seed_areas.py
from db.session import SessionLocal
from models.models import Area

# Datos base
AREAS = [
    {"nombre": "Mantención"},
    {"nombre": "Nutrición y Alimentación"},
    {"nombre": "Limpieza"},
    {"nombre": "Asistencia Social"},
    {"nombre": "Acompañamiento Espiritual"},
]

def seed_areas():
    db = SessionLocal()
    try:
        for area in AREAS:
            exists = db.query(Area).filter(Area.nombre == area["nombre"]).first()
            if not exists:
                db.add(Area(**area))
        db.commit()
        print("✅ Áreas insertadas correctamente")
    finally:
        db.close()

if __name__ == "__main__":
    seed_areas()
