from __future__ import annotations

import os

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://mongo_admin:password@localhost:27017/?authSource=admin",
)
MONGODB_DB = os.getenv("MONGODB_DB", "library")
MONGODB_BOOKS_COLLECTION = os.getenv("MONGODB_BOOKS_COLLECTION", "books")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "password")
