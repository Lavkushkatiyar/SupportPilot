from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependancy import get_db
from app.core.security import create_access_token
from app.schemas.auth import (
    UserLogin,
    UserLoginResponse,
    UserRegistration,
    UserRegistrationResponse,
)
from app.services.auth import authenticate_user, create_user

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


@router.post("/login", response_model=UserLoginResponse)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    # Implement login logic here
    pass
    user = authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(user.id)
    return UserLoginResponse(access_token=access_token)
