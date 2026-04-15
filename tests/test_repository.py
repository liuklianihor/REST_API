from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from app.repository.book_repository import MongoBookRepository
from app.schemas.book_schema import BookCreate, BookStatus


class FakeCursor:
    def __init__(self, docs):
        self.docs = docs
        self.query = None
        self.sort_args = None
        self.skip_value = None
        self.limit_value = None

    def sort(self, field, direction):
        self.sort_args = (field, direction)
        return self

    def skip(self, value):
        self.skip_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    async def to_list(self, length):
        return self.docs[:length]


@pytest.mark.asyncio
async def test_repository_builds_mongo_query():
    collection = SimpleNamespace()
    cursor = FakeCursor([{"_id": ObjectId(), "title": "A", "author": "Alice", "description": "D", "status": "available", "year": 2024}])
    collection.find = MagicMock(return_value=cursor)

    repo = MongoBookRepository(collection)
    books = await repo.list_books(limit=10, offset=0, author="Alice", status=BookStatus.available, sort_by="title")

    collection.find.assert_called_once_with({"author": "Alice", "status": "available"})
    assert cursor.sort_args[0] == "title"
    assert books[0].author == "Alice"


@pytest.mark.asyncio
async def test_repository_create_and_delete():
    inserted_id = ObjectId()
    collection = SimpleNamespace(
        insert_one=AsyncMock(return_value=SimpleNamespace(inserted_id=inserted_id)),
        find_one=AsyncMock(return_value={
            "_id": inserted_id,
            "title": "Book",
            "author": "Author",
            "description": "Desc",
            "status": "available",
            "year": 2024,
        }),
        delete_one=AsyncMock(return_value=SimpleNamespace(deleted_count=1)),
    )

    repo = MongoBookRepository(collection)
    created = await repo.create_book(BookCreate(
        title="Book",
        author="Author",
        description="Desc",
        status=BookStatus.available,
        year=2024,
    ))
    assert created.id == inserted_id

    deleted = await repo.delete_book(inserted_id)
    assert deleted is True
