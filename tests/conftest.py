from __future__ import annotations

from typing import Generator

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.api.auth import router as auth_router
from app.api.books import get_book_service
from app.models.book_model import BookDocument
from app.schemas.book_schema import BookCreate, BookStatus
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
        return items[offset : offset + limit]

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


@pytest.fixture()
def fake_service() -> InMemoryBookService:
    return InMemoryBookService()


@pytest.fixture()
def client(fake_service: InMemoryBookService) -> Generator[TestClient, None, None]:
    def override_get_book_service():
        return fake_service

    app.dependency_overrides[get_book_service] = override_get_book_service
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
