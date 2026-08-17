from datetime import datetime
from pydantic import BaseModel, ConfigDict , HttpUrl , Field


#Create Paper Schema



class PaperCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=500
    )

    abstract: str = Field(
        min_length=1
    )

    authors: str = Field(
        min_length=1,
        max_length=1000
    )

    publication_year: int = Field(
        ge=1900,
        le=2100
    )

    journal: str = Field(
        min_length=1,
        max_length=255
    )

    doi: str = Field(
        min_length=1,
        max_length=255
    )

    category: str = Field(
        min_length=1,
        max_length=100
    )

    pdf_url: HttpUrl





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
    title: str = Field(
        min_length=1,
        max_length=500
    )

    abstract: str = Field(
        min_length=1
    )

    authors: str = Field(
        min_length=1,
        max_length=1000
    )

    publication_year: int = Field(
        ge=1900,
        le=2100
    )

    journal: str = Field(
        min_length=1,
        max_length=255
    )

    doi: str = Field(
        min_length=1,
        max_length=255
    )

    category: str = Field(
        min_length=1,
        max_length=100
    )

    pdf_url: HttpUrl