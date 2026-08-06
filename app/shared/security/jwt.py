from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config.settings import settings


def create_access_token(data: dict) -> str:
    # Copy the payload so we don't modify the original dictionary
    to_encode = data.copy()

    # Set token expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Add expiration time to the payload
    to_encode.update({"exp": expire})

    # Create and sign the JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt