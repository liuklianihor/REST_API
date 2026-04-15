from __future__ import annotations

from pydantic_mongo import PydanticObjectId

from app.models.book_model import BookDocument
from app.repository.book_repository import MongoBookRepository
from app.schemas.book_schema import BookCreate, BookStatus


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
    ) -> list[BookDocument]:
        return await self.repository.list_books(
            limit=limit,
            offset=offset,
            author=author,
            status=status,
            sort_by=sort_by,
        )

    async def get_book(self, book_id: PydanticObjectId) -> BookDocument | None:
        return await self.repository.get_book_by_id(book_id)

    async def create_book(self, book_data: BookCreate) -> BookDocument:
        return await self.repository.create_book(book_data)

    async def delete_book(self, book_id: PydanticObjectId) -> bool:
        return await self.repository.delete_book(book_id)
