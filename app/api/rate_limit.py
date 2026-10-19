from fastapi import Depends, HTTPException, Request, status

from app.api.v1.auth_dependancies import get_current_user
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


def user_rate_limit(
    current_user=Depends(get_current_user),
) -> None:
    key = f"user:{current_user.id}"

    if not check_rate_limit(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
