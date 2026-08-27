from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


revision: str = '90c63cdc86be'
down_revision: Union[str, Sequence[str], None] = 'b1f6f67a8e7e'


def upgrade() -> None:
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column(
            'embedding',
            pgvector.sqlalchemy.vector.VECTOR(dim=384),
            nullable=False
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['paper_documents.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('document_chunks')