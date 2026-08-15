from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperCreate(BaseModel):
    title: str
    abstract: str | None = None
    content: str | None = None


class PaperResponse(BaseModel):
    id: int
    title: str
    abstract: str | None
    content: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)