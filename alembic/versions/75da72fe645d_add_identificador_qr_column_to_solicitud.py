"""add identificador_qr column to solicitud

Revision ID: 75da72fe645d
Revises: 9bba27e475a8
Create Date: 2025-09-30 23:53:50.922200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75da72fe645d'
down_revision: Union[str, Sequence[str], None] = '9bba27e475a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Agregar columna como NULLABLE (para no romper filas existentes)
    op.add_column(
        "solicitud",
        sa.Column("identificador_qr", sa.String(), nullable=True),
    )

    # 2) Backfill: copiar el QR desde la tabla cama
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE solicitud s
            SET identificador_qr = c.identificador_qr
            FROM cama c
            WHERE s.id_cama = c.id_cama
              AND s.identificador_qr IS NULL
            """
        )
    )

    # (opcional) índice para filtrar por QR rápido
    op.create_index("ix_solicitud_identificador_qr", "solicitud", ["identificador_qr"])

    # 3) Volverla obligatoria (NOT NULL) una vez que ya tiene datos
    op.alter_column(
        "solicitud",
        "identificador_qr",
        existing_type=sa.String(),
        nullable=False,
    )


def downgrade() -> None:
    # Revertir NOT NULL no es necesario explícito; con drop se elimina
    op.drop_index("ix_solicitud_identificador_qr", table_name="solicitud")
    op.drop_column("solicitud", "identificador_qr")