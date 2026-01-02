"""add token budget tracking to agent_runs

Revision ID: 3d32acd673b8
Revises: ebe7e97312f5
Create Date: 2025-12-30 17:28:58.975398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3d32acd673b8'
down_revision: Union[str, Sequence[str], None] = 'ebe7e97312f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Add columns as NULLABLE first
    op.add_column(
        "agent_runs",
        sa.Column("estimated_tokens_used", sa.Integer(), nullable=True),
    )

    op.add_column(
        "agent_runs",
        sa.Column("budget_exceeded", sa.Boolean(), nullable=True),
    )

    # 2️⃣ Backfill existing rows
    op.execute(
        "UPDATE agent_runs SET estimated_tokens_used = 0 WHERE estimated_tokens_used IS NULL"
    )

    op.execute(
        "UPDATE agent_runs SET budget_exceeded = FALSE WHERE budget_exceeded IS NULL"
    )

    # 3️⃣ Enforce NOT NULL
    op.alter_column(
        "agent_runs",
        "estimated_tokens_used",
        nullable=False,
    )

    op.alter_column(
        "agent_runs",
        "budget_exceeded",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("agent_runs", "budget_exceeded")
    op.drop_column("agent_runs", "estimated_tokens_used")