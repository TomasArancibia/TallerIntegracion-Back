"""Refactor timestamps: add fecha_actualizacion/cierre, drop intermedias
Revision ID: f7e8d9c0a123
Revises: a1b2c3d4e5f6   # ← tu última revisión
Create Date: 2025-10-02
"""
from alembic import op
import sqlalchemy as sa

revision = "f7e8d9c0a123"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

def upgrade():
    # 1) Nuevas columnas
    op.add_column(
        "solicitud",
        sa.Column("fecha_actualizacion", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"))
    )
    op.add_column(
        "solicitud",
        sa.Column("fecha_cierre", sa.DateTime(), nullable=True)
    )

    # 2) Backfill de fecha_actualizacion = fecha_creacion si está NULL (por compatibilidad)
    op.execute("""
        UPDATE solicitud
        SET fecha_actualizacion = COALESCE(fecha_actualizacion, fecha_creacion)
    """)

    # 3) Backfill de fecha_cierre desde columnas antiguas
    #    (si existían valores previos en resuelta/cancelada)
    op.execute("""
        UPDATE solicitud
        SET fecha_cierre = COALESCE(fecha_resuelta, fecha_cancelada)
        WHERE fecha_cierre IS NULL
    """)

    # 4) Eliminar columnas antiguas
    with op.batch_alter_table("solicitud") as batch:
        # Si estas columnas no existen en tu DB por algún motivo, comenta el drop correspondiente
        batch.drop_column("fecha_en_proceso")
        batch.drop_column("fecha_resuelta")
        batch.drop_column("fecha_cancelada")

# 5) Reglas de coherencia (CHECKs) — normalizamos el ENUM a texto minúscula
    op.execute("""
        ALTER TABLE solicitud
        ADD CONSTRAINT ck_solicitud_cierre_por_estado
        CHECK (
            (LOWER(estado_actual::text) IN ('abierto','en_proceso') AND fecha_cierre IS NULL)
            OR
            (LOWER(estado_actual::text) IN ('resuelto','cancelado') AND fecha_cierre IS NOT NULL)
        )
    """)

def downgrade():
    # Quitar CHECK
    op.execute("ALTER TABLE solicitud DROP CONSTRAINT IF EXISTS ck_solicitud_cierre_por_estado")

    # Re-crear columnas antiguas (vacías)
    with op.batch_alter_table("solicitud") as batch:
        batch.add_column(sa.Column("fecha_cancelada", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("fecha_resuelta", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("fecha_en_proceso", sa.DateTime(), nullable=True))

    # Intento de backfill inverso (no perfecto, pero razonable)
    op.execute("""
        UPDATE solicitud
        SET fecha_resuelta = CASE WHEN estado_actual='resuelto' THEN fecha_cierre ELSE NULL END,
            fecha_cancelada = CASE WHEN estado_actual='cancelado' THEN fecha_cierre ELSE NULL END
    """)

    # Quitar nuevas columnas
    with op.batch_alter_table("solicitud") as batch:
        batch.drop_column("fecha_cierre")
        batch.drop_column("fecha_actualizacion")
