from sqlalchemy import create_engine

from app.config.settings import settings


DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{settings.DATABASE_USER}:"
    f"{settings.DATABASE_PASSWORD}@"
    f"{settings.DATABASE_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.DATABASE_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
)