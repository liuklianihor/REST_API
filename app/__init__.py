from __future__ import annotations

import atexit

from flask import Flask, jsonify
from flask_restful import Api
from flasgger import Swagger
from flask.wrappers import Response as FlaskResponse

from app.api.books import BookItemResource, BookListResource
from app.core.config import MONGODB_BOOKS_COLLECTION, MONGODB_DB, MONGODB_URI
from app.core.database import create_mongo_client
from app.repository.book_repository import MongoBookRepository
from app.services.book_service import BookService


class JsonDict(dict):
    def __call__(self):
        return self


class JsonList(list):
    def __call__(self):
        return self


class CompatResponse(FlaskResponse):
    @property
    def json(self):
        payload = self.get_json()

        if isinstance(payload, dict):
            return JsonDict(payload)

        if isinstance(payload, list):
            return JsonList(payload)

        return payload


def _swagger_config() -> dict:
    return {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }


def _swagger_template() -> dict:
    return {
        "swagger": "2.0",
        "info": {
            "title": "Library API",
            "description": "Swagger documentation for the existing library endpoints.",
            "version": "1.0.0",
        },
        "basePath": "/",
        "schemes": ["http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "tags": [
            {"name": "Books", "description": "Book management endpoints"},
        ],
        "definitions": {
            "BookCreate": {
                "type": "object",
                "required": ["title", "author", "description", "status", "year"],
                "properties": {
                    "title": {"type": "string", "example": "Clean Code"},
                    "author": {"type": "string", "example": "Robert C. Martin"},
                    "description": {
                        "type": "string",
                        "example": "A handbook of agile software craftsmanship.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["available", "borrowed"],
                        "example": "available",
                    },
                    "year": {"type": "integer", "example": 2008},
                },
            },
            "BookRead": {
                "allOf": [
                    {"$ref": "#/definitions/BookCreate"},
                    {
                        "type": "object",
                        "required": ["id"],
                        "properties": {
                            "id": {
                                "type": "string",
                                "example": "66c4d2c4b25a6f9c1b6b2d10",
                            }
                        },
                    },
                ]
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "array",
                                "items": {"type": "object"},
                            },
                        ]
                    }
                },
            },
        },
        "paths": {
            "/books": {
                "get": {
                    "tags": ["Books"],
                    "summary": "List books",
                    "parameters": [
                        {
                            "name": "author",
                            "in": "query",
                            "type": "string",
                            "required": False,
                            "description": "Filter by author.",
                        },
                        {
                            "name": "status",
                            "in": "query",
                            "type": "string",
                            "required": False,
                            "enum": ["available", "borrowed"],
                            "description": "Filter by book status.",
                        },
                        {
                            "name": "sort_by",
                            "in": "query",
                            "type": "string",
                            "required": False,
                            "enum": ["title", "year"],
                            "description": "Sort by title or year.",
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "type": "integer",
                            "required": False,
                            "default": 10,
                            "description": "Page size, from 1 to 100.",
                        },
                        {
                            "name": "offset",
                            "in": "query",
                            "type": "integer",
                            "required": False,
                            "default": 0,
                            "description": "Starting offset, must be non-negative.",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "List of books",
                            "schema": {
                                "type": "array",
                                "items": {"$ref": "#/definitions/BookRead"},
                            },
                        },
                        "400": {
                            "description": "Invalid query parameters",
                            "schema": {"$ref": "#/definitions/ErrorResponse"},
                        },
                    },
                },
                "post": {
                    "tags": ["Books"],
                    "summary": "Create a book",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/BookCreate"},
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Created book",
                            "schema": {"$ref": "#/definitions/BookRead"},
                        },
                        "400": {
                            "description": "Invalid request body",
                            "schema": {"$ref": "#/definitions/ErrorResponse"},
                        },
                    },
                },
            },
            "/books/{book_id}": {
                "get": {
                    "tags": ["Books"],
                    "summary": "Get a book by id",
                    "parameters": [
                        {
                            "name": "book_id",
                            "in": "path",
                            "type": "string",
                            "required": True,
                            "description": "Book identifier.",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Book found",
                            "schema": {"$ref": "#/definitions/BookRead"},
                        },
                        "404": {
                            "description": "Book not found",
                            "schema": {"$ref": "#/definitions/ErrorResponse"},
                        },
                    },
                },
                "delete": {
                    "tags": ["Books"],
                    "summary": "Delete a book by id",
                    "parameters": [
                        {
                            "name": "book_id",
                            "in": "path",
                            "type": "string",
                            "required": True,
                            "description": "Book identifier.",
                        }
                    ],
                    "responses": {
                        "204": {"description": "Book deleted"},
                    },
                },
            },
        },
    }


def create_app(config_overrides: dict | None = None, repository=None) -> Flask:
    app = Flask(__name__)
    app.response_class = CompatResponse

    app.config.update(
        TESTING=False,
        MONGODB_URI=MONGODB_URI,
        MONGODB_DB=MONGODB_DB,
        MONGODB_BOOKS_COLLECTION=MONGODB_BOOKS_COLLECTION,
    )

    if config_overrides:
        app.config.update(config_overrides)

    Swagger(app, config=_swagger_config(), template=_swagger_template())

    if repository is None:
        mongo_client = create_mongo_client(app.config["MONGODB_URI"])
        app.extensions["mongo_client"] = mongo_client

        collection = mongo_client[app.config["MONGODB_DB"]][app.config["MONGODB_BOOKS_COLLECTION"]]
        repository = MongoBookRepository(collection)

        atexit.register(mongo_client.close)

    service = BookService(repository)
    app.extensions["book_service"] = service

    api = Api(app)
    api.add_resource(BookListResource, "/books", "/books/")
    api.add_resource(BookItemResource, "/books/<string:book_id>", "/books/<string:book_id>/")

    @app.get("/")
    def index():
        return jsonify(
            {
                "message": "Library API",
                "swagger": "/apidocs/",
                "books": "/books/",
            }
        )

    return app
