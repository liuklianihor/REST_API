from __future__ import annotations

import asyncio

from app.schemas.book_schema import BookCreate, BookStatus


def _run(coro):
    return asyncio.run(coro)


class BookService:
    def __init__(self, repository):
        self.repository = repository

    def list_books(
        self,
        *,
        limit: int,
        offset: int,
        author: str | None = None,
        status: BookStatus | None = None,
        sort_by: str | None = None,
    ):
        return _run(
            self.repository.list_books(
                limit=limit,
                offset=offset,
                author=author,
                status=status,
                sort_by=sort_by,
            )
        )

    def get_book(self, book_id: str):
        return _run(self.repository.get_book_by_id(book_id))

    def create_book(self, book_data: BookCreate):
        return _run(self.repository.create_book(book_data))

    def delete_book(self, book_id: str):
        return _run(self.repository.delete_book(book_id))
