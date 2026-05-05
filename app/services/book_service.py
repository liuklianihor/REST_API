from __future__ import annotations

import asyncio

from app.schemas.book_schema import (
    BookCreate,
    BookPage,
    BookRead,
    BookStatus,
    PaginationInfo,
)


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
    ) -> BookPage:
        books = _run(
            self.repository.list_books(
                limit=limit,
                offset=offset,
                author=author,
                status=status,
                sort_by=sort_by,
            )
        )

        count_method = getattr(self.repository, "count_books", None)
        if callable(count_method):
            total = _run(
                count_method(
                    author=author,
                    status=status,
                    sort_by=sort_by,
                )
            )
        else:
            total = offset + len(books)

        items = [
            BookRead.model_validate(book.model_dump(mode="json"))
            for book in books
        ]

        count = len(items)
        has_prev = offset > 0
        has_more = offset + count < total

        pagination = PaginationInfo(
            limit=limit,
            offset=offset,
            count=count,
            total=total,
            has_more=has_more,
            has_prev=has_prev,
            next_offset=(offset + limit) if has_more else None,
            prev_offset=max(offset - limit, 0) if has_prev else None,
        )

        return BookPage(items=items, pagination=pagination)

    def get_book(self, book_id: str):
        return _run(self.repository.get_book_by_id(book_id))

    def create_book(self, book_data: BookCreate):
        return _run(self.repository.create_book(book_data))

    def delete_book(self, book_id: str):
        return _run(self.repository.delete_book(book_id))