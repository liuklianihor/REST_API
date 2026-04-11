import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app
from app.models.book_model import books_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_books_db():
    books_db.clear()
    yield
    books_db.clear()


def build_book(title="Test Book", author="Test Author", description="Test Description", status="available", year=2024):
    return {
        "title": title,
        "author": author,
        "description": description,
        "status": status,
        "year": year,
    }


def test_create_book():
    response = client.post("/books/", json=build_book())

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert "id" in data


def test_get_books():
    client.post("/books/", json=build_book())
    response = client.get("/books/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_get_book_by_id():
    create_response = client.post("/books/", json=build_book())
    book_id = create_response.json()["id"]

    response = client.get(f"/books/{book_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Test Book"


def test_filter_by_author():
    client.post("/books/", json=build_book(author="Alice"))
    client.post("/books/", json=build_book(title="Other", author="Bob"))

    response = client.get("/books/?author=Alice")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Alice"


def test_sort_by_title():
    client.post("/books/", json=build_book(title="Z Book"))
    client.post("/books/", json=build_book(title="A Book"))

    response = client.get("/books/?sort_by=title")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["title"] == "A Book"
    assert data[1]["title"] == "Z Book"


def test_delete_book_is_idempotent():
    create_response = client.post("/books/", json=build_book(title="Delete Book"))
    book_id = create_response.json()["id"]

    first_delete = client.delete(f"/books/{book_id}")
    second_delete = client.delete(f"/books/{book_id}")

    assert first_delete.status_code == 204
    assert second_delete.status_code == 204
