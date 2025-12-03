"""
Redis caching utilities.
"""

import json
from typing import Optional, Any
from redis import Redis
from functools import wraps

from app.config import settings


class CacheService:
    """Redis cache service."""

    def __init__(self):
        self._client: Optional[Redis] = None

    @property
    def client(self) -> Redis:
        """Get Redis client (lazy initialization)."""
        if self._client is None:
            self._client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        return self._client

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache."""
        if ttl is None:
            ttl = settings.REDIS_CACHE_TTL_DEFAULT

        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        return self.client.setex(key, ttl, value)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return bool(self.client.delete(key))

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(self.client.exists(key))

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0

    def incr(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        return self.client.incr(key, amount)

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on a key."""
        return self.client.expire(key, ttl)


# Global cache instance
cache = CacheService()


def cached(
    key_prefix: str,
    ttl: Optional[int] = None,
):
    """
    Decorator for caching function results.

    Usage:
        @cached("player", ttl=300)
        def get_player(player_id: int):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
