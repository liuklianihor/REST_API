from __future__ import annotations


def build_book(
    title="Test Book",
    author="Test Author",
    description="Test Description",
    status="available",
    year=2024,
):
    return {
        "title": title,
        "author": author,
        "description": description,
        "status": status,
        "year": year,
    }


def test_create_book(client):
    response = client.post("/books/", json=build_book())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert "id" in data


def test_get_books(client):
    client.post("/books/", json=build_book())
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 1


def test_get_book_by_id(client):
    create_response = client.post("/books/", json=build_book())
    book_id = create_response.json()["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Test Book"


def test_filter_by_author(client):
    client.post("/books/", json=build_book(author="Alice"))
    client.post("/books/", json=build_book(title="Other", author="Bob"))
    response = client.get("/books/?author=Alice")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["author"] == "Alice"


def test_sort_by_title(client):
    client.post("/books/", json=build_book(title="Z Book"))
    client.post("/books/", json=build_book(title="A Book"))
    response = client.get("/books/?sort_by=title")
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["title"] == "A Book"
    assert data["items"][1]["title"] == "Z Book"


def test_cursor_pagination(client):
    client.post("/books/", json=build_book(title="Book 1"))
    client.post("/books/", json=build_book(title="Book 2"))
    client.post("/books/", json=build_book(title="Book 3"))

    first_page = client.get("/books/?limit=2&sort_by=title")
    assert first_page.status_code == 200
    first_data = first_page.json()
    assert len(first_data["items"]) == 2
    assert first_data["next_cursor"] is not None
    assert first_data["has_more"] is True

    second_page = client.get(
        f"/books/?limit=2&sort_by=title&cursor={first_data['next_cursor']}"
    )
    assert second_page.status_code == 200
    second_data = second_page.json()
    assert len(second_data["items"]) == 1
    assert second_data["items"][0]["title"] == "Book 3"
    assert second_data["has_more"] is False


def test_delete_book_is_idempotent(client):
    create_response = client.post("/books/", json=build_book(title="Delete Book"))
    book_id = create_response.json()["id"]

    first_delete = client.delete(f"/books/{book_id}")
    second_delete = client.delete(f"/books/{book_id}")

    assert first_delete.status_code == 204
    assert second_delete.status_code == 204
