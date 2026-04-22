from __future__ import annotations

import time
import uuid

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.config import RATE_LIMITER_ENABLED
from app.core.security import get_current_user

RATE_LIMITS: dict[str, tuple[int, int]] = {
    "anonymous": (2, 60),
    "authenticated": (10, 60),
}

def get_redis(request: Request) -> Redis:
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return redis_client

async def _apply_rate_limit(redis: Redis, identity: str, limit: int, period: int) -> None:
    key = f"rate_limit:{identity}"
    now = int(time.time())
    window_start = now - period

    await redis.zremrangebyscore(key, min=0, max=window_start)
    request_count = await redis.zcard(key)

    if request_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )

    await redis.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
    await redis.expire(key, period)

async def rate_limit_anonymous(
    request: Request,
    redis: Redis = Depends(get_redis),
) -> None:
    if not RATE_LIMITER_ENABLED:
        return

    identity = request.client.host if request.client else "anonymous"
    limit, period = RATE_LIMITS["anonymous"]
    await _apply_rate_limit(redis, identity, limit, period)

async def rate_limit_authenticated(
    user_id: str = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
) -> None:
    if not RATE_LIMITER_ENABLED:
        return

    limit, period = RATE_LIMITS["authenticated"]
    await _apply_rate_limit(redis, user_id, limit, period)
