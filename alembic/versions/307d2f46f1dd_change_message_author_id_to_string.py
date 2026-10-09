"""change message author id to string

Revision ID: 307d2f46f1dd
Revises: df7a7f5936a1
Create Date: 2026-10-09 16:16:16.135971

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "307d2f46f1dd"
down_revision: str | Sequence[str] | None = "df7a7f5936a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "messages",
        "author_id",
        existing_type=sa.BigInteger(),
        type_=sa.String(),
        existing_nullable=False,
        postgresql_using="author_id::text",
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
