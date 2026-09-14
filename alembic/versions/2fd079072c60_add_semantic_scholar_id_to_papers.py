"""add semantic scholar id to papers

Revision ID: 2fd079072c60
Revises: 2c2a3eda6baa
Create Date: 2026-09-14 00:09:11.616677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2fd079072c60'
down_revision: Union[str, Sequence[str], None] = '2c2a3eda6baa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "papers",
        sa.Column(
            "semantic_scholar_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_papers_semantic_scholar_id",
        "papers",
        ["semantic_scholar_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_papers_semantic_scholar_id",
        "papers",
        type_="unique",
    )

    op.drop_column(
        "papers",
        "semantic_scholar_id",
    )
