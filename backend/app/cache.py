import os
import redis

CACHE_TTL_SECONDS = 60 * 60 * 24 * 180
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_client = None

def get_redis():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    return _client

def cache_key(short_code: str) -> str:
    return f"url:{short_code}"

def get_cached_url(short_code: str):
    client = get_redis()
    value = client.get(cache_key(short_code))
    if value is not None:
        # Expiração deslizante: o acesso renova os 180 dias.
        client.expire(cache_key(short_code), CACHE_TTL_SECONDS)
    return value

def cache_url(short_code: str, original_url: str):
    get_redis().setex(cache_key(short_code), CACHE_TTL_SECONDS, original_url)

def get_ttl(short_code: str) -> int:
    return get_redis().ttl(cache_key(short_code))
