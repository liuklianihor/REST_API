from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.book_schema import Book, BookCreate, BookStatus
from app.services.book_service import erase_book, fetch_book, list_books, persist_book

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[Book])
async def read_books(
    author: Optional[str] = Query(default=None),
    status: Optional[BookStatus] = Query(default=None),
    sort_by: Optional[str] = Query(default=None, pattern="^(title|year)$"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    books = await list_books(
        db,
        limit=limit,
        offset=offset,
        author=author,
        status=status,
        sort_by=sort_by,
    )

    return books

@router.get("/{book_id}", response_model=Book)
async def read_book(book_id: UUID, db: Session = Depends(get_db)):
    book = await fetch_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=Book, status_code=201)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return await persist_book(db, book)


@router.delete("/{book_id}", status_code=204)
async def remove_book(book_id: UUID, db: Session = Depends(get_db)):
    await erase_book(db, book_id)
    return None
