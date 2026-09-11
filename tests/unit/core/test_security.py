from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_returns_hashed_value() -> None:
    password = "super-secret-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert isinstance(hashed_password, str)
    assert hashed_password


def test_verify_password_returns_true_for_matching_password() -> None:
    password = "super-secret-password"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    password = "super-secret-password"
    hashed_password = hash_password(password)

    assert verify_password("wrong-password", hashed_password) is False


def test_create_access_token_and_decode_access_token() -> None:
    user_id = 123
    token = create_access_token(user_id)

    assert isinstance(token, str)
    assert token

    decoded_payload = decode_access_token(token)

    assert decoded_payload["sub"] == str(user_id)
    assert decoded_payload["type"] == "access"


def test_access_token_contains_expected_claims() -> None:
    token = create_access_token(1)

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload
