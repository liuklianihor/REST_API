from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.auth import router as auth_router
from app.api.books import router as books_router
from app.core.config import REDIS_URL
from app.core.database import create_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mongo_client = create_mongo_client()
    app.state.redis = Redis.from_url(REDIS_URL, decode_responses=True)
    yield
    app.state.mongo_client.close()
    await app.state.redis.aclose()


app = FastAPI(title="Library API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(books_router)
