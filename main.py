from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.books import router as books_router
from app.core.database import create_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mongo_client = create_mongo_client()
    yield
    app.state.mongo_client.close()


app = FastAPI(title="Library API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(books_router)
