from __future__ import annotations

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.core.config import MONGODB_BOOKS_COLLECTION, MONGODB_DB, MONGODB_URI


def create_mongo_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(MONGODB_URI)


async def get_mongo_client(request: Request) -> AsyncIOMotorClient:
    return request.app.state.mongo_client


def get_database(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> AsyncIOMotorDatabase:
    return client[MONGODB_DB]


def get_book_collection(
    database: AsyncIOMotorDatabase = Depends(get_database),
) -> AsyncIOMotorCollection:
    return database[MONGODB_BOOKS_COLLECTION]
