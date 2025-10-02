"""Saneamiento: UNIQUEs + NOT NULL + índices + default en fecha_creacion
Revision ID: a1b2c3d4e5f6
Revises: 75da72fe645d
Create Date: 2025-10-02
"""
from alembic import op
import sqlalchemy as sa

# Identificadores requeridos por Alembic
revision = "a1b2c3d4e5f6"      # <-- cualquier ID único (hex/alfanumérico)
down_revision = "75da72fe645d"  # <-- TU última migración válida (la que me mostraste)
branch_labels = None
depends_on = None


def upgrade():
    # --- AREA: nombre único
    op.create_unique_constraint("uq_area_nombre", "area", ["nombre"])

    # --- HABITACION: (hospital, numero) único
    op.create_unique_constraint(
        "uq_habitacion_hospital_numero",
        "habitacion",
        ["id_hospital", "numero"],
    )

    # --- CAMA: índices útiles
    op.create_index("ix_cama_id_habitacion", "cama", ["id_habitacion"])
    op.create_index("ix_cama_activo", "cama", ["activo"])

    # --- SOLICITUD: índices más consultados
    op.create_index("ix_solicitud_estado", "solicitud", ["estado_actual"])
    op.create_index("ix_solicitud_fecha_creacion", "solicitud", ["fecha_creacion"])
    op.create_index("ix_solicitud_id_cama", "solicitud", ["id_cama"])

    # --- SOLICITUD: reforzar NOT NULLs
    op.alter_column("solicitud", "id_cama", nullable=False, existing_type=sa.Integer())
    op.alter_column("solicitud", "id_area", nullable=False, existing_type=sa.Integer())
    op.alter_column("solicitud", "identificador_qr", nullable=False, existing_type=sa.String())
    op.alter_column("solicitud", "tipo", nullable=False, existing_type=sa.String())

    # --- SOLICITUD: estado_actual NOT NULL (sin asumir nombre del enum)
    op.execute("ALTER TABLE solicitud ALTER COLUMN estado_actual SET NOT NULL")

    # --- SOLICITUD: fecha_creacion con default NOW()
    op.alter_column(
        "solicitud",
        "fecha_creacion",
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_type=sa.DateTime(),
    )


def downgrade():
    # Quitar default
    op.alter_column(
        "solicitud",
        "fecha_creacion",
        server_default=None,
        existing_type=sa.DateTime(),
    )

    # Revertir índices
    op.drop_index("ix_solicitud_id_cama", table_name="solicitud")
    op.drop_index("ix_solicitud_fecha_creacion", table_name="solicitud")
    op.drop_index("ix_solicitud_estado", table_name="solicitud")
    op.drop_index("ix_cama_activo", table_name="cama")
    op.drop_index("ix_cama_id_habitacion", table_name="cama")

    # Quitar UNIQUEs
    op.drop_constraint("uq_habitacion_hospital_numero", "habitacion", type_="unique")
    op.drop_constraint("uq_area_nombre", "area", type_="unique")
