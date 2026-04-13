from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"


class BookBase(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1)
    status: BookStatus
    year: int = Field(ge=0)


class BookCreate(BookBase):
    pass


class Book(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
