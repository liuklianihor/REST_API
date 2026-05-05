from __future__ import annotations

from typing import Generator

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.api.books import get_book_service
from app.core.rate_limiter import get_redis
from app.models.book_model import BookDocument
from app.schemas.book_schema import BookCreate, BookPage, BookRead, BookStatus, PaginationInfo
from main import app


class InMemoryBookService:
    def __init__(self):
        self.books: list[BookDocument] = []

    async def list_books(self, *, limit, offset, author=None, status=None, sort_by=None):
        items = self.books

        if author:
            items = [book for book in items if book.author == author]
        if status:
            items = [book for book in items if book.status == status]

        if sort_by == "title":
            items = sorted(items, key=lambda book: book.title)
        elif sort_by == "year":
            items = sorted(items, key=lambda book: book.year)
        else:
            items = sorted(items, key=lambda book: str(book.id))

        total = len(items)
        paged_items = items[offset : offset + limit]

        page_items = [
            BookRead.model_validate(book.model_dump(mode="python"))
            for book in paged_items
        ]

        count = len(page_items)
        has_prev = offset > 0
        has_more = offset + count < total

        return BookPage(
            items=page_items,
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

    async def get_book(self, book_id):
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    async def create_book(self, book_data: BookCreate):
        book = BookDocument(id=ObjectId(), **book_data.model_dump())
        self.books.append(book)
        return book

    async def delete_book(self, book_id):
        self.books = [book for book in self.books if book.id != book_id]
        return True


class FakeRedis:
    def __init__(self) -> None:
        self._zsets: dict[str, dict[str, int]] = {}

    async def zremrangebyscore(self, key: str, min: int = 0, max: int = 0) -> int:
        bucket = self._zsets.get(key, {})
        to_remove = [member for member, score in bucket.items() if min <= score <= max]
        for member in to_remove:
            del bucket[member]
        return len(to_remove)

    async def zcard(self, key: str) -> int:
        return len(self._zsets.get(key, {}))

    async def zadd(self, key: str, mapping: dict[str, int]) -> int:
        bucket = self._zsets.setdefault(key, {})
        bucket.update(mapping)
        return len(mapping)

    async def expire(self, key: str, period: int) -> bool:
        return True


@pytest.fixture()
def fake_service() -> InMemoryBookService:
    return InMemoryBookService()


@pytest.fixture()
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture()
def client(fake_service: InMemoryBookService, fake_redis: FakeRedis) -> Generator[TestClient, None, None]:
    def override_get_book_service():
        return fake_service

    def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_book_service] = override_get_book_service
    app.dependency_overrides[get_redis] = override_get_redis

    with TestClient(app) as test_client:
        login_response = test_client.post(
            "/auth/token",
            data={"username": "admin", "password": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def anonymous_client(fake_service: InMemoryBookService, fake_redis: FakeRedis) -> Generator[TestClient, None, None]:
    def override_get_book_service():
        return fake_service

    def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_book_service] = override_get_book_service
    app.dependency_overrides[get_redis] = override_get_redis

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()