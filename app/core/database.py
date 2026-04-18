from __future__ import annotations

from pymongo import MongoClient


def create_mongo_client(uri: str) -> MongoClient:
    return MongoClient(uri, serverSelectionTimeoutMS=2000)
