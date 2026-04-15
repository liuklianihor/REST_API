from __future__ import annotations

from typing import Optional

from pydantic_mongo import PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING

from app.models.book_model import BookDocument
from app.schemas.book_schema import BookCreate, BookStatus


class MongoBookRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def list_books(
        self,
        *,
        limit: int,
        offset: int,
        author: Optional[str] = None,
        status: Optional[BookStatus] = None,
        sort_by: Optional[str] = None,
    ) -> list[BookDocument]:
        query: dict = {}
        if author:
            query["author"] = author
        if status:
            query["status"] = status.value

        sort_field = "_id"
        if sort_by == "title":
            sort_field = "title"
        elif sort_by == "year":
            sort_field = "year"

        cursor = (
            self.collection.find(query)
            .sort(sort_field, ASCENDING)
            .skip(offset)
            .limit(limit)
        )
        documents = await cursor.to_list(length=limit)
        return [BookDocument.from_mongo(document) for document in documents if document is not None]

    async def get_book_by_id(self, book_id: PydanticObjectId) -> BookDocument | None:
        document = await self.collection.find_one({"_id": book_id})
        return BookDocument.from_mongo(document)

    async def create_book(self, book_data: BookCreate) -> BookDocument:
        payload = book_data.model_dump(mode="python")
        result = await self.collection.insert_one(payload)
        document = await self.collection.find_one({"_id": result.inserted_id})
        if document is None:
            return BookDocument(id=result.inserted_id, **book_data.model_dump())
        return BookDocument.from_mongo(document)

    async def delete_book(self, book_id: PydanticObjectId) -> bool:
        result = await self.collection.delete_one({"_id": book_id})
        return result.deleted_count > 0
