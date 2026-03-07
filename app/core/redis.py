"""
Redis Client Configuration
"""
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from typing import Optional

from app.core.config import settings


class RedisClient:
    """Redis client singleton"""
    
    _pool: Optional[ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    
    @classmethod
    async def get_pool(cls) -> ConnectionPool:
        """Get or create connection pool"""
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
            )
        return cls._pool
    
    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get Redis client"""
        if cls._client is None:
            pool = await cls.get_pool()
            cls._client = redis.Redis(connection_pool=pool)
        return cls._client
    
    @classmethod
    async def close(cls):
        """Close Redis connections"""
        if cls._client:
            await cls._client.close()
        if cls._pool:
            await cls._pool.disconnect()


async def get_redis() -> redis.Redis:
    """Dependency for FastAPI routes"""
    return await RedisClient.get_client()
