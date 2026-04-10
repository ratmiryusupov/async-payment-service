"""add webhook status to payments

Revision ID: 12dc4eadc3fd
Revises: e725c12f8f3b
Create Date: 2026-04-09 21:35:40.168409
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "12dc4eadc3fd"
down_revision: Union[str, Sequence[str], None] = "e725c12f8f3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


webhook_status_enum = sa.Enum(
    "PENDING",
    "DELIVERED",
    "FAILED",
    name="webhook_status_enum",
)


def upgrade() -> None:
    webhook_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "payments",
        sa.Column(
            "webhook_status",
            webhook_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
    )


def downgrade() -> None:
    op.drop_column("payments", "webhook_status")
    webhook_status_enum.drop(op.get_bind(), checkfirst=True)