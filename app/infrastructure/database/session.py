from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.config import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)