from __future__ import annotations

import inspect
from typing import Optional

from bson import ObjectId
from pymongo import ASCENDING

from app.models.book_model import BookDocument
from app.schemas.book_schema import BookCreate, BookStatus


async def _maybe_await(value):
    if inspect.isawaitable(value):
        return await value
    return value


class MongoBookRepository:
    def __init__(self, collection):
        self.collection = collection

    def _build_query(
        self,
        *,
        author: Optional[str] = None,
        status: Optional[BookStatus] = None,
    ) -> dict:
        query: dict = {}
        if author:
            query["author"] = author
        if status:
            query["status"] = status.value
        return query

    async def count_books(
        self,
        *,
        author: Optional[str] = None,
        status: Optional[BookStatus] = None,
        sort_by: Optional[str] = None,
    ) -> int:
        query = self._build_query(author=author, status=status)
        count = self.collection.count_documents(query)
        count = await _maybe_await(count)
        return int(count)

    async def list_books(
        self,
        *,
        limit: int,
        offset: int,
        author: Optional[str] = None,
        status: Optional[BookStatus] = None,
        sort_by: Optional[str] = None,
    ) -> list[BookDocument]:
        query = self._build_query(author=author, status=status)

        sort_field = "_id"
        if sort_by == "title":
            sort_field = "title"
        elif sort_by == "year":
            sort_field = "year"

        cursor = (
            self.collection.find(query)
            .sort(sort_field, ASCENDING)
            .skip(offset)
            .limit(limit)
        )

        if hasattr(cursor, "to_list"):
            documents = await _maybe_await(cursor.to_list(length=limit))
        else:
            documents = list(cursor)

        return [
            book
            for book in (BookDocument.from_mongo(document) for document in documents)
            if book is not None
        ]

    async def get_book_by_id(self, book_id: str) -> BookDocument | None:
        if not ObjectId.is_valid(book_id):
            return None

        document = await _maybe_await(self.collection.find_one({"_id": ObjectId(book_id)}))
        return BookDocument.from_mongo(document)

    async def create_book(self, book_data: BookCreate) -> BookDocument:
        payload = book_data.model_dump(mode="json")
        result = await _maybe_await(self.collection.insert_one(payload))
        document = await _maybe_await(self.collection.find_one({"_id": result.inserted_id}))

        if document is None:
            return BookDocument(id=result.inserted_id, **book_data.model_dump())

        return BookDocument.from_mongo(document)

    async def delete_book(self, book_id: str) -> bool:
        if not ObjectId.is_valid(book_id):
            return False

        result = await _maybe_await(self.collection.delete_one({"_id": ObjectId(book_id)}))
        return result.deleted_count > 0