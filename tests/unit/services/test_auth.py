from unittest.mock import MagicMock

import pytest

from app.core.security import hash_password
from app.models.user import User
from app.services.auth import authenticate_user, create_user


def test_create_user_adds_and_returns_user() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    user = create_user(db, "new@example.com", "secret-password")

    assert user.email == "new@example.com"
    assert user.password_hash != "secret-password"
    db.add.assert_called_once_with(user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_create_user_rejects_duplicate_email() -> None:
    db = MagicMock()
    db.scalar.return_value = User(
        email="existing@example.com",
        password_hash=hash_password("secret-password"),
    )

    with pytest.raises(ValueError, match="User already exists"):
        create_user(db, "existing@example.com", "secret-password")

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_authenticate_user_returns_user_for_valid_credentials() -> None:
    user = User(
        email="member@example.com",
        password_hash=hash_password("secret-password"),
    )
    db = MagicMock()
    db.scalar.return_value = user

    result = authenticate_user(db, "member@example.com", "secret-password")

    assert result is user


def test_authenticate_user_returns_none_for_wrong_password() -> None:
    user = User(
        email="member@example.com",
        password_hash=hash_password("secret-password"),
    )
    db = MagicMock()
    db.scalar.return_value = user

    result = authenticate_user(db, "member@example.com", "wrong-password")

    assert result is None


def test_authenticate_user_returns_none_for_unknown_email() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    result = authenticate_user(db, "unknown@example.com", "secret-password")

    assert result is None
