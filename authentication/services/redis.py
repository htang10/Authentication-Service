from urllib.parse import urlparse

import redis
from django.conf import settings


def redis_instance() -> redis.Redis:
    """Initiates and returns a Redis instance."""
    url = urlparse(settings.REDIS_URL)
    return redis.Redis(host=url.hostname, port=url.port or 6379, decode_responses=True)
