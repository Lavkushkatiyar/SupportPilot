from fastapi import HTTPException, Request, status

from app.services.rate_limiter import check_rate_limit


def rate_limit(request: Request) -> None:
    if request.client is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client IP address not found.",
        )

    client_ip = request.client.host
    allowed = check_rate_limit(client_ip)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
