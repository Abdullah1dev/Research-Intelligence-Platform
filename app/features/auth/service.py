from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.users.models import User

from app.shared.security.hashing import (
    hash_password,
    verify_password,
)

from app.features.auth.schemas import (
    RegisterRequest,
    LoginRequest,
)

from app.shared.enums.roles import UserRole


def register_user(
    data: RegisterRequest,
    db: Session,
) -> User:

    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if existing_user:
        raise ValueError(
            "Email already registered"
        )

    hashed_password = hash_password(
        data.password
    )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_password,
        role=UserRole.RESEARCHER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    data: LoginRequest,
) -> User:

    user = db.scalar(
        select(User).where(
            User.email == data.email
        )
    )

    if user is None:
        raise ValueError(
            "Invalid email or password"
        )

    result = verify_password(
        data.password,
        user.password_hash,
    )

    if not result:
        raise ValueError(
            "Invalid email or password"
        )

    return user