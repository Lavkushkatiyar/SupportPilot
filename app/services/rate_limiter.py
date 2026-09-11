from app.core.config import settings
from app.core.redis import redis_client


def check_rate_limit(identifier: str) -> bool:
    key = f"rate_limit:{identifier}"
    current_count = redis_client.incr(key)
    if current_count == 1:
        redis_client.expire(
            key,
            settings.rate_limit_window_seconds,
        )

    return current_count <= settings.rate_limit_requests
