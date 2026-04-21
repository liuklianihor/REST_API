from __future__ import annotations


def _login_form():
    return {
        "username": "admin",
        "password": "password",
    }


def test_anonymous_user_under_limit_gets_200(anonymous_client):
    response = anonymous_client.post(
        "/auth/token",
        data=_login_form(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200


def test_anonymous_user_at_limit_gets_429(anonymous_client):
    for _ in range(2):
        response = anonymous_client.post(
            "/auth/token",
            data=_login_form(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

    response = anonymous_client.post(
        "/auth/token",
        data=_login_form(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 429


def test_authenticated_user_under_limit_gets_200(client):
    response = client.get("/books")
    assert response.status_code == 200


def test_authenticated_user_at_limit_gets_429(client):
    for _ in range(10):
        response = client.get("/books")
        assert response.status_code == 200

    response = client.get("/books")
    assert response.status_code == 429
