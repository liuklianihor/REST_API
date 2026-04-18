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
            "description": "Library API built with Flask-RESTful and Flasgger.",
            "version": "1.0.0",
        },
        "basePath": "/",
        "schemes": ["http"],
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
