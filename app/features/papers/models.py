from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.users.models import User


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    abstract: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    authors: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    publication_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    journal: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    doi: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    pdf_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
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

    owner: Mapped["User"] = relationship(
        back_populates="papers"
    )