from urllib.parse import urlparse

import redis
from django.conf import settings


def redis_instance() -> redis.Redis:
    url = urlparse(settings.REDIS_URL)
    return redis.Redis(host=url.hostname, port=url.port, decode_responses=True)
