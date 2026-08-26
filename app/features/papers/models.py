from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text , Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.users.models import User

from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum
from app.features.papers.enums import DocumentProcessingStatus
from pgvector.sqlalchemy import Vector

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
    
    document = relationship(
    "PaperDocument",
    back_populates="paper",
    uselist=False,
    cascade="all, delete-orphan"
    )




#Paper Document Modle
class PaperDocument(Base):
    __tablename__ = "paper_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    mime_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    storage_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    paper = relationship(
        "Paper",
        back_populates="document"
    )
    
    processing_status = Column(
        SQLEnum(
            DocumentProcessingStatus,
            values_callable=lambda enum_class: [member.value for member in enum_class],
            name="documentprocessingstatus",  
               
            ),
        nullable=False,
        default=DocumentProcessingStatus.PENDING,
    )
   
    
    
    processing_error = Column(
    Text,
    nullable=True,
    )
    
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)

    document_id = Column(
        Integer,
        ForeignKey("paper_documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    embedding = Column(
        Vector(384),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )