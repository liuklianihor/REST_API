from __future__ import annotations

import base64
import json
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, asc, or_, select
from sqlalchemy.orm import Session

from app.models.book_model import Book
from app.schemas.book_schema import BookCreate, BookPage, BookStatus


def _encode_cursor(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _decode_cursor(cursor: str) -> dict[str, object]:
    padding = "=" * (-len(cursor) % 4)
    raw = base64.urlsafe_b64decode((cursor + padding).encode("utf-8"))
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid cursor")
    return data


def list_books(
    db: Session,
    *,
    limit: int,
    cursor: Optional[str] = None,
    author: Optional[str] = None,
    status: Optional[BookStatus] = None,
    sort_by: Optional[str] = None,
) -> BookPage:
    query = select(Book)

    if author:
        query = query.where(Book.author == author)

    if status:
        query = query.where(Book.status == status.value)

    if sort_by == "title":
        query = query.order_by(asc(Book.title), asc(Book.id))
        if cursor:
            data = _decode_cursor(cursor)
            cursor_title = str(data["title"])
            cursor_id = UUID(str(data["id"]))
            query = query.where(
                or_(
                    Book.title > cursor_title,
                    and_(Book.title == cursor_title, Book.id > cursor_id),
                )
            )
    elif sort_by == "year":
        query = query.order_by(asc(Book.year), asc(Book.id))
        if cursor:
            data = _decode_cursor(cursor)
            cursor_year = int(data["year"])
            cursor_id = UUID(str(data["id"]))
            query = query.where(
                or_(
                    Book.year > cursor_year,
                    and_(Book.year == cursor_year, Book.id > cursor_id),
                )
            )
    else:
        query = query.order_by(asc(Book.id))
        if cursor:
            data = _decode_cursor(cursor)
            cursor_id = UUID(str(data["id"]))
            query = query.where(Book.id > cursor_id)

    rows = db.execute(query.limit(limit + 1)).scalars().all()
    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        if sort_by == "title":
            next_cursor = _encode_cursor({"title": last.title, "id": str(last.id)})
        elif sort_by == "year":
            next_cursor = _encode_cursor({"year": last.year, "id": str(last.id)})
        else:
            next_cursor = _encode_cursor({"id": str(last.id)})

    return BookPage(items=items, next_cursor=next_cursor, has_more=has_more)


def get_book_by_id(db: Session, book_id):
    return db.get(Book, book_id)


def create_book(db: Session, book_data: BookCreate):
    book = Book(**book_data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id):
    book = db.get(Book, book_id)
    if book is None:
        return False
    db.delete(book)
    db.commit()
    return True
