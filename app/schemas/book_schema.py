from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from pydantic_mongo import PydanticObjectId


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
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: PydanticObjectId


class PaginationInfo(BaseModel):
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    count: int = Field(ge=0)
    total: int = Field(ge=0)
    has_more: bool = False
    has_prev: bool = False
    next_offset: int | None = None
    prev_offset: int | None = None


class BookPage(BaseModel):
    items: list[BookRead]
    pagination: PaginationInfo