from __future__ import annotations

from pydantic_mongo import PydanticObjectId

from app.models.book_model import BookDocument
from app.repository.book_repository import MongoBookRepository
from app.schemas.book_schema import (
    BookCreate,
    BookPage,
    BookRead,
    BookStatus,
    PaginationInfo,
)


class BookService:
    def __init__(self, repository: MongoBookRepository):
        self.repository = repository

    async def list_books(
        self,
        *,
        limit: int,
        offset: int,
        author: str | None = None,
        status: BookStatus | None = None,
        sort_by: str | None = None,
    ) -> BookPage:
        books = await self.repository.list_books(
            limit=limit,
            offset=offset,
            author=author,
            status=status,
            sort_by=sort_by,
        )

        count_method = getattr(self.repository, "count_books", None)
        if callable(count_method):
            total = await count_method(
                author=author,
                status=status,
                sort_by=sort_by,
            )
        else:
            total = offset + len(books)

        items = [
            BookRead.model_validate(book.model_dump(mode="python"))
            for book in books
        ]
        count = len(items)
        has_prev = offset > 0
        has_more = offset + count < total

        return BookPage(
            items=items,
            pagination=PaginationInfo(
                limit=limit,
                offset=offset,
                count=count,
                total=total,
                has_more=has_more,
                has_prev=has_prev,
                next_offset=(offset + limit) if has_more else None,
                prev_offset=max(offset - limit, 0) if has_prev else None,
            ),
        )

    async def get_book(self, book_id: PydanticObjectId) -> BookDocument | None:
        return await self.repository.get_book_by_id(book_id)

    async def create_book(self, book_data: BookCreate) -> BookDocument:
        return await self.repository.create_book(book_data)

    async def delete_book(self, book_id: PydanticObjectId) -> bool:
        return await self.repository.delete_book(book_id)