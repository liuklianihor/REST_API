from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.repository.book_repository import (
    create_book as repo_create_book,
    delete_book as repo_delete_book,
    get_book_by_id as repo_get_book_by_id,
    list_books as repo_list_books,
)
from app.schemas.book_schema import BookCreate, BookPage, BookStatus


async def list_books(
    db: Session,
    *,
    limit: int,
    cursor: Optional[str] = None,
    author: Optional[str] = None,
    status: Optional[BookStatus] = None,
    sort_by: Optional[str] = None,
) -> BookPage:
    return await repo_list_books(
        db,
        limit=limit,
        cursor=cursor,
        author=author,
        status=status,
        sort_by=sort_by,
    )


async def fetch_book(db: Session, book_id: UUID):
    return await repo_get_book_by_id(db, book_id)


async def persist_book(db: Session, book_data: BookCreate):
    return await repo_create_book(db, book_data)


async def erase_book(db: Session, book_id: UUID):
    return await repo_delete_book(db, book_id)
