import enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.session import Base


class RolUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    JEFE_AREA = "JEFE_AREA"


class EstadoSolicitud(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    CERRADA = "cerrada"


class Institucion(Base):
    __tablename__ = "institucion"

    id_institucion = Column(Integer, primary_key=True, index=True)
    nombre_institucion = Column(String(120), nullable=False, unique=True)

    edificios = relationship("Edificio", back_populates="institucion")


class Edificio(Base):
    __tablename__ = "edificio"
    __table_args__ = (
        UniqueConstraint("id_institucion", "nombre_edificio", name="ux_edificio"),
    )

    id_edificio = Column(Integer, primary_key=True, index=True)
    nombre_edificio = Column(String(120), nullable=False)
    id_institucion = Column(Integer, ForeignKey("institucion.id_institucion"), nullable=False)

    institucion = relationship("Institucion", back_populates="edificios")
    pisos = relationship("Piso", back_populates="edificio")


class Piso(Base):
    __tablename__ = "piso"
    __table_args__ = (
        UniqueConstraint("id_edificio", "numero_piso", name="ux_piso"),
    )

    id_piso = Column(Integer, primary_key=True, index=True)
    numero_piso = Column(Integer, nullable=False)
    id_edificio = Column(Integer, ForeignKey("edificio.id_edificio"), nullable=False)

    edificio = relationship("Edificio", back_populates="pisos")
    habitaciones = relationship("Habitacion", back_populates="piso")


class Servicio(Base):
    __tablename__ = "servicio"

    id_servicio = Column(Integer, primary_key=True, index=True)
    nombre_servicio = Column(String(120), nullable=False, unique=True)

    habitaciones = relationship("Habitacion", back_populates="servicio")


class Area(Base):
    __tablename__ = "area"

    id_area = Column(Integer, primary_key=True, index=True)
    nombre_area = Column(String(120), nullable=False, unique=True)

    solicitudes = relationship("Solicitud", back_populates="area")
    usuarios = relationship("Usuario", back_populates="area")


class Habitacion(Base):
    __tablename__ = "habitacion"
    __table_args__ = (
        UniqueConstraint("id_piso", "nombre_habitacion", name="ux_habitacion"),
    )

    id_habitacion = Column(Integer, primary_key=True, index=True)
    nombre_habitacion = Column(String(50), nullable=False)
    id_piso = Column(Integer, ForeignKey("piso.id_piso"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("servicio.id_servicio"), nullable=False)

    piso = relationship("Piso", back_populates="habitaciones")
    servicio = relationship("Servicio", back_populates="habitaciones")
    camas = relationship("Cama", back_populates="habitacion")


class Cama(Base):
    __tablename__ = "cama"
    __table_args__ = (
        UniqueConstraint("id_habitacion", "letra_cama", name="ux_cama_por_hab"),
    )

    id_cama = Column(Integer, primary_key=True, index=True)
    letra_cama = Column(String(4), nullable=False)
    id_habitacion = Column(Integer, ForeignKey("habitacion.id_habitacion"), nullable=False)
    identificador_qr = Column(String(32), nullable=False, unique=True)
    activo = Column(Boolean, nullable=False, default=True)

    habitacion = relationship("Habitacion", back_populates="camas")
    solicitudes = relationship("Solicitud", back_populates="cama")


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(UUID(as_uuid=True), primary_key=True)
    rol = Column(
        SAEnum(
            RolUsuario,
            name="rol_usuario",
            create_type=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    correo = Column(String(160), nullable=False, unique=True)
    nombre = Column(String(80), nullable=False)
    apellido = Column(String(80), nullable=False)
    telefono = Column(String(30))
    id_area = Column(Integer, ForeignKey("area.id_area"), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    actualizado_en = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))

    area = relationship("Area", back_populates="usuarios")


class Solicitud(Base):
    __tablename__ = "solicitud"

    id_solicitud = Column(Integer, primary_key=True, index=True)
    id_cama = Column(Integer, ForeignKey("cama.id_cama"), nullable=False)
    id_area = Column(Integer, ForeignKey("area.id_area"), nullable=False)
    tipo = Column(String(120), nullable=False)
    descripcion = Column(String)
    estado_actual = Column(
        SAEnum(
            EstadoSolicitud,
            name="estado_solicitud",
            create_type=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    fecha_actualizacion = Column(DateTime(timezone=True))
    fecha_cierre = Column(DateTime(timezone=True))
    nombre_solicitante = Column(String(120))
    correo_solicitante = Column(String(160))

    cama = relationship("Cama", back_populates="solicitudes")
    area = relationship("Area", back_populates="solicitudes")
