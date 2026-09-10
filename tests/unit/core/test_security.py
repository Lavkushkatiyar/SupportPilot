from app.core.security import hash_password, verify_password


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
