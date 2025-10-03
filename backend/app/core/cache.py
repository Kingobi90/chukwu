"""Redis caching utilities"""

from typing import Optional, Any
import json
from redis import asyncio as aioredis

from app.core.config import settings

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf8",
            decode_responses=True
        )
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    redis = await get_redis()
    value = await redis.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_set(key: str, value: Any, expire: int = 300) -> None:
    """Set value in cache with expiration (seconds)"""
    redis = await get_redis()
    await redis.setex(key, expire, json.dumps(value))


async def cache_delete(key: str) -> None:
    """Delete key from cache"""
    redis = await get_redis()
    await redis.delete(key)


async def cache_clear_pattern(pattern: str) -> None:
    """Clear all keys matching pattern"""
    redis = await get_redis()
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)
