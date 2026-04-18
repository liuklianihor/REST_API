from __future__ import annotations

from typing import Optional

from sqlalchemy import UUID, asc, desc, select
from sqlalchemy.orm import Session

from app.models.book_model import Book
from app.schemas.book_schema import BookCreate, BookStatus


async def list_books(
    db: Session,
    *,
    limit: int,
    offset: int,
    author: Optional[str] = None,
    status: Optional[BookStatus] = None,
    sort_by: Optional[str] = None,
):
    query = select(Book)

    if author:
        query = query.where(Book.author == author)

    if status:
        query = query.where(Book.status == status.value)

    if sort_by == "title":
        query = query.order_by(asc(Book.title))
    elif sort_by == "year":
        query = query.order_by(asc(Book.year))
    else:
        query = query.order_by(asc(Book.id))

    query = query.offset(offset).limit(limit)
    return db.execute(query).scalars().all()


async def get_book_by_id(db: Session, book_id: UUID):
    return db.get(Book, book_id)


async def create_book(db: Session, book_data: BookCreate):
    book = Book(**book_data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


async def delete_book(db: Session, book_id: UUID):
    book = db.get(Book, book_id)
    if book is None:
        return False

    db.delete(book)
    db.commit()
    return True
