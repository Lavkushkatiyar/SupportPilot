from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependancy import get_db
from app.schemas.auth import UserRegistration, UserRegistrationResponse
from app.services.auth import create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegistration,
    db: Session = Depends(get_db),
):
    try:
        user = create_user(
            db=db,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return user
