"""add user role

Revision ID: 4506c11dc116
Revises: 9a8f7762e048
Create Date: 2026-08-07 23:47:06.300973

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4506c11dc116"
down_revision: Union[str, Sequence[str], None] = "9a8f7762e048"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create the PostgreSQL enum type first.
    user_role_enum = sa.Enum(
        "admin",
        "researcher",
        "reviewer",
        name="userrole",
    )

    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Add the role column.
    #
    # Existing users will receive "researcher".
    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            nullable=False,
            server_default="researcher",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove the role column first.
    op.drop_column("users", "role")

    # Then remove the PostgreSQL enum type.
    user_role_enum = sa.Enum(
        "admin",
        "researcher",
        "reviewer",
        name="userrole",
    )

    user_role_enum.drop(op.get_bind(), checkfirst=True)