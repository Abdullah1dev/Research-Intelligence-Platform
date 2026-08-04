from fastapi import FastAPI

from app.features.auth.router import router as auth_router


from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(auth_router)