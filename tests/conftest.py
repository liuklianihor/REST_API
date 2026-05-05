from __future__ import annotations

from bson import ObjectId
import pytest

from app import create_app
from app.models.book_model import BookDocument


class AsyncInMemoryBookRepository:
    def __init__(self):
        self._books: dict[str, BookDocument] = {}
        self._counter = 1

    async def count_books(self, *, author=None, status=None, sort_by=None):
        books = list(self._books.values())

        if author is not None:
            books = [book for book in books if book.author == author]
        if status is not None:
            books = [book for book in books if book.status == status]

        return len(books)

    async def list_books(self, *, limit, offset, author=None, status=None, sort_by=None):
        books = list(self._books.values())

        if author is not None:
            books = [book for book in books if book.author == author]
        if status is not None:
            books = [book for book in books if book.status == status]

        if sort_by == "title":
            books.sort(key=lambda book: book.title)
        elif sort_by == "year":
            books.sort(key=lambda book: book.year)

        return books[offset:offset + limit]

    async def get_book_by_id(self, book_id):
        return self._books.get(book_id)

    async def create_book(self, book_data):
        book_id = ObjectId()
        book = BookDocument(
            id=book_id,
            title=book_data.title,
            author=book_data.author,
            description=book_data.description,
            status=book_data.status,
            year=book_data.year,
        )
        self._books[str(book_id)] = book
        return book

    async def delete_book(self, book_id):
        return self._books.pop(book_id, None) is not None


@pytest.fixture()
def app():
    repository = AsyncInMemoryBookRepository()
    app = create_app({"TESTING": True}, repository=repository)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
