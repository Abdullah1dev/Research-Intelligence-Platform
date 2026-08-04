from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.users.models import User
from app.shared.security.hashing import hash_password
from app.features.auth.schemas import RegisterRequest


def register_user(
    data: RegisterRequest,
    db: Session,
) -> User:
    # Check whether the email already exists
    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if existing_user:
        raise ValueError("Email already registered")

    # Hash the plain password
    hashed_password = hash_password(data.password)

    # Create the database user
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user