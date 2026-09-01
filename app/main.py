from fastapi import FastAPI

from app.features.auth.router import router as auth_router
from app.features.papers.router import router as papers_router
from app.features.conversations.router import (
    router as conversations_router,
)


from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(auth_router)

app.include_router(papers_router)

app.include_router(conversations_router)