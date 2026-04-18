from __future__ import annotations

from flask import current_app, request
from flask_restful import Resource, abort
from pydantic import ValidationError

from app.schemas.book_schema import BookCreate, BookStatus


def _service():
    return current_app.extensions["book_service"]


def _serialize(book):
    return book.model_dump(mode="json")


def _parse_filters():
    author = request.args.get("author") or None
    status_raw = request.args.get("status") or None
    sort_by = request.args.get("sort_by") or None

    if sort_by not in (None, "title", "year"):
        abort(400, message="sort_by must be one of: title, year")

    status = None
    if status_raw is not None:
        try:
            status = BookStatus(status_raw)
        except ValueError:
            abort(400, message="status must be one of: available, borrowed")

    try:
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        abort(400, message="limit and offset must be integers")

    if not 1 <= limit <= 100:
        abort(400, message="limit must be between 1 and 100")
    if offset < 0:
        abort(400, message="offset must be greater than or equal to 0")

    return author, status, sort_by, limit, offset


class BookListResource(Resource):
    def get(self):
        author, status, sort_by, limit, offset = _parse_filters()
        books = _service().list_books(
            limit=limit,
            offset=offset,
            author=author,
            status=status,
            sort_by=sort_by,
        )
        return [_serialize(book) for book in books], 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        try:
            book_data = BookCreate.model_validate(payload)
        except ValidationError as exc:
            abort(400, message=exc.errors())

        book = _service().create_book(book_data)
        return _serialize(book), 201


class BookItemResource(Resource):
    def get(self, book_id: str):
        book = _service().get_book(book_id)
        if book is None:
            abort(404, message="Book not found")
        return _serialize(book), 200

    def delete(self, book_id: str):
        _service().delete_book(book_id)
        return "", 204
