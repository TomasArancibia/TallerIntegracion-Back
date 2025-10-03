"""Rename 'ABIERTO' to 'pendiente' (y demás valores a minúscula) en estadosolicitud"""

from alembic import op

# Revisar IDs previos
revision = "g1h2i3j4k5l6"
down_revision = "f7e8d9c0a123"  # tu última revisión
branch_labels = None
depends_on = None


def upgrade():
    # 1) Elimina la CHECK previa si existe (para no chocar)
    op.execute("ALTER TABLE solicitud DROP CONSTRAINT IF EXISTS ck_solicitud_cierre_por_estado;")

    # 2) Renombra labels del enum de MAYÚSCULA → minúscula
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'ABIERTO' TO 'pendiente';")
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'EN_PROCESO' TO 'en_proceso';")
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'RESUELTO' TO 'resuelto';")
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'CANCELADO' TO 'cancelado';")

    # 3) Recrea la CHECK constraint con los nuevos labels
    op.execute("""
        ALTER TABLE solicitud
        ADD CONSTRAINT ck_solicitud_cierre_por_estado
        CHECK (
            (estado_actual IN ('pendiente','en_proceso') AND fecha_cierre IS NULL)
            OR
            (estado_actual IN ('resuelto','cancelado') AND fecha_cierre IS NOT NULL)
        )
    """)


def downgrade():
    # 1) Quita la CHECK actual
    op.execute("ALTER TABLE solicitud DROP CONSTRAINT IF EXISTS ck_solicitud_cierre_por_estado;")

    # 2) Vuelve a poner los labels en MAYÚSCULA (rollback)
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'pendiente' TO 'ABIERTO';")
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'en_proceso' TO 'EN_PROCESO';")
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'resuelto' TO 'RESUELTO';")
    op.execute("ALTER TYPE estadosolicitud RENAME VALUE 'cancelado' TO 'CANCELADO';")

    # 3) Restaura la CHECK con los valores originales
    op.execute("""
        ALTER TABLE solicitud
        ADD CONSTRAINT ck_solicitud_cierre_por_estado
        CHECK (
            (estado_actual IN ('ABIERTO','EN_PROCESO') AND fecha_cierre IS NULL)
            OR
            (estado_actual IN ('RESUELTO','CANCELADO') AND fecha_cierre IS NOT NULL)
        )
    """)
