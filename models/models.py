from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db.session import Base
import enum

class EstadoSolicitud(str, enum.Enum):
    ABIERTO = "abierto"
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

    tipo = Column(String, nullable=False)
    descripcion = Column(String)
    estado_actual = Column(Enum(EstadoSolicitud), default=EstadoSolicitud.ABIERTO)

    fecha_creacion = Column(DateTime)
    fecha_en_proceso = Column(DateTime)
    fecha_resuelta = Column(DateTime)
    fecha_cancelada = Column(DateTime)

    cama = relationship("Cama", back_populates="solicitudes")
    area = relationship("Area", back_populates="solicitudes")
