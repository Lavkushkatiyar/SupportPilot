from app.core.redis import redis_client
from app.services.rate_limiter import check_rate_limit


def test_rate_limit_allows_requests_within_limit() -> None:
    identifier = "test-client-allowed"
    redis_client.delete(f"rate_limit:{identifier}")

    results = [check_rate_limit(identifier) for _ in range(10)]

    assert all(results)


def test_rate_limit_rejects_requests_over_limit() -> None:
    identifier = "test-client-rejected"
    redis_client.delete(f"rate_limit:{identifier}")

    results = [check_rate_limit(identifier) for _ in range(12)]

    assert results[:10] == [True] * 10
    assert results[10:] == [False, False]
