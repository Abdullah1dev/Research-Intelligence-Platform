from datetime import datetime
from pydantic import BaseModel, ConfigDict , HttpUrl , Field
from app.features.papers.enums import DocumentProcessingStatus



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
    
    
class PaginatedPaperResponse(BaseModel):
    items: list[PaperResponse]
    page: int
    limit: int
    total: int
    total_pages: int
    

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
    
    


class PaperDocumentResponse(BaseModel):
    id: int
    paper_id: int
    file_name: str
    file_size: int
    mime_type: str
    storage_key: str

    processing_status: DocumentProcessingStatus
    processing_error: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
    

class PaperQuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the paper",
    )
    
    
    


class PaperSourceResponse(BaseModel):

    chunk_id: int

    chunk_index: int

    content: str

    similarity_score: float


class PaperQuestionResponse(BaseModel):

    paper_id: int

    document_id: int

    question: str

    answer: str

    sources: list[PaperSourceResponse]
    

#Paper Summary Response
class PaperSummaryResponse(BaseModel):

    paper_id: int

    document_id: int

    summary: str