from __future__ import annotations

import os

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://mongo_admin:password@localhost:27017/?authSource=admin",
)
MONGODB_DB = os.getenv("MONGODB_DB", "library")
MONGODB_BOOKS_COLLECTION = os.getenv("MONGODB_BOOKS_COLLECTION", "books")
