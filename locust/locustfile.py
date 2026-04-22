from __future__ import annotations

import os

from locust import HttpUser, between, task


class AuthTokenUser(HttpUser):
    wait_time = between(1, 2)
    host = os.getenv("LOCUST_HOST", "http://api:8000")
    username = os.getenv("LOCUST_USERNAME", "admin")
    password = os.getenv("LOCUST_PASSWORD", "password")

    @task
    def obtain_token(self) -> None:
        payload = {
            "username": self.username,
            "password": self.password,
        }

        with self.client.post(
            "/auth/token",
            data=payload,
            name="POST /auth/token",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status code: {response.status_code}")
                return

            try:
                body = response.json()
            except ValueError:
                response.failure("Response is not valid JSON")
                return

            if not isinstance(body, dict):
                response.failure("Expected a JSON object in the response")
                return

            if not body.get("access_token") or not body.get("refresh_token"):
                response.failure("Token pair is incomplete")
                return

            response.success()
