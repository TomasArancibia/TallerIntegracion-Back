import enum
from sqlalchemy import Column, Integer, String, Enum as SAEnum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.session import Base

class EstadoSolicitud(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    CANCELADO = "cancelado"

class Hospital(Base):
    __tablename__ = "hospital"
    id_hospital = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    habitaciones = relationship("Habitacion", back_populates="hospital")

class Habitacion(Base):
    __tablename__ = "habitacion"
    id_habitacion = Column(Integer, primary_key=True, index=True)
    numero = Column(String, nullable=False)
    id_hospital = Column(Integer, ForeignKey("hospital.id_hospital"), nullable=False)
    hospital = relationship("Hospital", back_populates="habitaciones")
    camas = relationship("Cama", back_populates="habitacion")

class Cama(Base):
    __tablename__ = "cama"
    id_cama = Column(Integer, primary_key=True, index=True)
    identificador_qr = Column(String, nullable=False, unique=True)
    id_habitacion = Column(Integer, ForeignKey("habitacion.id_habitacion"), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    habitacion = relationship("Habitacion", back_populates="camas")
    solicitudes = relationship("Solicitud", back_populates="cama")

class Area(Base):
    __tablename__ = "area"
    id_area = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    solicitudes = relationship("Solicitud", back_populates="area")

class Solicitud(Base):
    __tablename__ = "solicitud"

    id_solicitud = Column(Integer, primary_key=True, index=True)
    id_cama = Column(Integer, ForeignKey("cama.id_cama"), nullable=False)
    id_area = Column(Integer, ForeignKey("area.id_area"), nullable=False)
    identificador_qr = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    descripcion = Column(String)

    # 👇 CLAVE: usa los VALUES del Enum de Python para mapear al Enum nativo de Postgres
    estado_actual = Column(
        SAEnum(
            EstadoSolicitud,
            name="estadosolicitud",
            create_type=False,  # ya existe en la BD
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )

    fecha_creacion = Column(DateTime)
    fecha_actualizacion = Column(DateTime)
    fecha_cierre = Column(DateTime)

    cama = relationship("Cama")
    area = relationship("Area")
