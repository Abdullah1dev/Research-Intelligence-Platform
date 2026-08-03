from app.shared.security.hashing import (
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "Research@123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("WrongPassword", hashed_password) is False