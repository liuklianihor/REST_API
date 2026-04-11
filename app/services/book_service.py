from uuid import uuid4
from app.repository.book_repository import (
    add_book,
    delete_book as remove_book_record,
    get_all_books,
    get_book_by_id,
)


async def list_books():
    return await get_all_books()


async def fetch_book(book_id):
    return await get_book_by_id(book_id)


async def persist_book(book_data):
    payload = book_data.model_dump()
    payload["id"] = uuid4()

    await add_book(payload)
    return payload


async def erase_book(book_id):
    return await remove_book_record(book_id)
