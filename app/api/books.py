from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.schemas.book_schema import Book, BookCreate, BookStatus
from app.services.book_service import erase_book, fetch_book, list_books, persist_book

router = APIRouter(prefix="/books", tags=["Books"])


def _apply_filters(items, author: Optional[str], status: Optional[BookStatus]):
    filtered = items

    if author:
        filtered = [book for book in filtered if book["author"] == author]

    if status:
        filtered = [book for book in filtered if book["status"] == status.value]

    return filtered


def _apply_sort(items, sort_by: Optional[str]):
    if sort_by == "title":
        return sorted(items, key=lambda item: item["title"])

    if sort_by == "year":
        return sorted(items, key=lambda item: item["year"])

    return items


@router.get("/", response_model=list[Book])
async def read_books(
    author: Optional[str] = Query(default=None),
    status: Optional[BookStatus] = Query(default=None),
    sort_by: Optional[str] = Query(default=None),
):
    books = await list_books()
    books = _apply_filters(books, author, status)
    books = _apply_sort(books, sort_by)
    return books


@router.get("/{book_id}", response_model=Book)
async def read_book(book_id: UUID):
    book = await fetch_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=Book, status_code=201)
async def create_book(book: BookCreate):
    return await persist_book(book)


@router.delete("/{book_id}", status_code=204)
async def remove_book(book_id: UUID):
    await erase_book(book_id)
    return None
