from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.book_schema import Book, BookCreate, BookPage, BookStatus
from app.services.book_service import erase_book, fetch_book, list_books, persist_book

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=BookPage)
def read_books(
    author: Optional[str] = Query(default=None),
    status: Optional[BookStatus] = Query(default=None),
    sort_by: Optional[str] = Query(default=None, pattern="^(title|year)$"),
    limit: int = Query(default=10, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        return list_books(
            db,
            limit=limit,
            cursor=cursor,
            author=author,
            status=status,
            sort_by=sort_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{book_id}", response_model=Book)
def read_book(book_id: UUID, db: Session = Depends(get_db)):
    book = fetch_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=Book, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return persist_book(db, book)


@router.delete("/{book_id}", status_code=204)
def remove_book(book_id: UUID, db: Session = Depends(get_db)):
    erase_book(db, book_id)
    return None
