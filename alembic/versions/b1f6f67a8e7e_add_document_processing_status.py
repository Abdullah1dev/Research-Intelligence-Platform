"""add document processing status

Revision ID: b1f6f67a8e7e
Revises: e105a31f39ef
Create Date: 2026-08-23 ...
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b1f6f67a8e7e"
down_revision: Union[str, Sequence[str], None] = "e105a31f39ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    document_processing_status = postgresql.ENUM(
        "pending",
        "processing",
        "completed",
        "failed",
        name="documentprocessingstatus",
        create_type=False,
    )

    document_processing_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "paper_documents",
        sa.Column(
            "processing_status",
            document_processing_status,
            nullable=False,
            server_default="pending",
        ),
    )

    op.add_column(
        "paper_documents",
        sa.Column(
            "processing_error",
            sa.Text(),
            nullable=True,
        ),
    )

    op.alter_column(
        "paper_documents",
        "processing_status",
        server_default=None,
    )


def downgrade():
    op.drop_column(
        "paper_documents",
        "processing_error"
    )

    op.drop_column(
        "paper_documents",
        "processing_status"
    )

    document_processing_status = postgresql.ENUM(
        "pending",
        "processing",
        "completed",
        "failed",
        name="documentprocessingstatus",
    )

    document_processing_status.drop(
        op.get_bind(),
        checkfirst=True,
    )