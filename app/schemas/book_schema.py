from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class BookStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2000)
    status: BookStatus
    year: int = Field(ge=0, le=3000)


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: str
