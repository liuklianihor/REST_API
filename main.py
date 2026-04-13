from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.books import router as books_router
from app.core.database import Base, engine
from app.models import book_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Library API", lifespan=lifespan)
app.include_router(books_router)
