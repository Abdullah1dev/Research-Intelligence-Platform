from datetime import datetime


from sqlalchemy.orm import Mapped, mapped_column , relationship

from app.infrastructure.database.base import Base

from sqlalchemy import String, DateTime, Boolean


from app.shared.enums.roles import UserRole
from sqlalchemy import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.papers.models import Paper



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            values_callable=lambda enum: [member.value for member in enum]
        ),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    papers: Mapped[list["Paper"]] = relationship(
        back_populates="owner"
    )
    
    
    conversations = relationship(
    "Conversation",
    back_populates="user",
    )
    