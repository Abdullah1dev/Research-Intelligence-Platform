from datetime import datetime

from pydantic import BaseModel, ConfigDict


#Create Paper Schema
class PaperCreate(BaseModel):
    title: str
    abstract: str | None = None
    authors: str
    publication_year: int | None = None
    journal: str | None = None
    doi: str | None = None
    category: str | None = None
    pdf_url: str | None = None


#Paper Response Schema
class PaperResponse(BaseModel):
    id: int
    title: str
    abstract: str | None
    authors: str
    publication_year: int | None
    journal: str | None
    doi: str | None
    category: str | None
    pdf_url: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    

#update paper Schema
class PaperUpdate(BaseModel):
    title: str
    abstract: str
    authors: str
    publication_year: int
    journal: str
    doi: str
    category: str
    pdf_url: str