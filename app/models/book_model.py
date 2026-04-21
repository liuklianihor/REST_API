from __future__ import annotations

from pydantic import ConfigDict
from pydantic_mongo import PydanticObjectId

from app.schemas.book_schema import BookBase


class BookDocument(BookBase):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: PydanticObjectId | None = None

    @classmethod
    def from_mongo(cls, document: dict | None) -> "BookDocument | None":
        if document is None:
            return None
        data = dict(document)
        data["id"] = data.pop("_id")
        return cls.model_validate(data)

    def to_mongo(self) -> dict:
        payload = self.model_dump(mode="python")
        if payload.get("id") is not None:
            payload["_id"] = payload.pop("id")
        return payload
