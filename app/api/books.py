from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic_mongo import PydanticObjectId

from app.core.database import get_book_collection
from app.core.rate_limiter import rate_limit_authenticated
from app.models.book_model import BookDocument
from app.repository.book_repository import MongoBookRepository
from app.schemas.book_schema import BookCreate, BookRead, BookStatus
from app.services.book_service import BookService

router = APIRouter(
    prefix="/books",
    tags=["Books"],
    dependencies=[Depends(rate_limit_authenticated)],
)


def get_book_repository(
    collection: AsyncIOMotorCollection = Depends(get_book_collection),
) -> MongoBookRepository:
    return MongoBookRepository(collection)


def get_book_service(
    repository: MongoBookRepository = Depends(get_book_repository),
) -> BookService:
    return BookService(repository)


@router.get("", response_model=list[BookRead])
async def read_books(
    author: str | None = Query(default=None),
    status: BookStatus | None = Query(default=None),
    sort_by: str | None = Query(default=None, pattern="^(title|year)$"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: BookService = Depends(get_book_service),
):
    return await service.list_books(
        limit=limit,
        offset=offset,
        author=author,
        status=status,
        sort_by=sort_by,
    )


@router.get("/{book_id}", response_model=BookRead)
async def read_book(
    book_id: PydanticObjectId,
    service: BookService = Depends(get_book_service),
):
    book = await service.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    service: BookService = Depends(get_book_service),
):
    return await service.create_book(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book(
    book_id: PydanticObjectId,
    service: BookService = Depends(get_book_service),
):
    await service.delete_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
