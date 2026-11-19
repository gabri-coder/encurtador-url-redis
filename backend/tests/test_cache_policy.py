from datetime import timedelta
from unittest.mock import Mock
from app import cache

def test_cache_ttl_is_180_days():
    assert cache.CACHE_TTL_SECONDS == 60 * 60 * 24 * 180

def test_cache_hit_renews_expiration(monkeypatch):
    fake = Mock()
    fake.get.return_value = "https://example.com"
    monkeypatch.setattr(cache, "get_redis", lambda: fake)
    assert cache.get_cached_url("abc") == "https://example.com"
    fake.expire.assert_called_once_with("url:abc", 60 * 60 * 24 * 180)

def test_cache_key_format():
    assert cache.cache_key("abc123") == "url:abc123"
