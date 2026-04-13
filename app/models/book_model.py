from __future__ import annotations

import uuid

from sqlalchemy import Integer, String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SAEnum

from app.core.database import Base
from app.schemas.book_schema import BookStatus


class GUID(TypeDecorator):
    """Platform-independent UUID type."""

    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value if dialect.name == "postgresql" else str(value)
        uuid_value = uuid.UUID(str(value))
        return uuid_value if dialect.name == "postgresql" else str(uuid_value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[BookStatus] = mapped_column(SAEnum(BookStatus, name="book_status", native_enum=False), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
