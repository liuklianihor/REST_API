from __future__ import annotations


def test_token_endpoint_returns_access_and_refresh(client):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_endpoint_issues_new_tokens(client):
    login = client.post(
        "/auth/token",
        data={"username": "admin", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data


def test_books_are_protected_without_token():
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as unauth_client:
        response = unauth_client.get("/books")
        assert response.status_code == 401
