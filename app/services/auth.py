from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


def create_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user is not None:
        raise ValueError("User already exists")

    user = User(
        email=email,
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = db.scalar(select(User).where(User.email == email))

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
