from sqlalchemy.orm import Session 
from sqlalchemy import select , func , or_  

from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate , PaperUpdate
from app.shared.enums.roles import UserRole
from app.features.users.models import User
from fastapi import HTTPException , UploadFile
from sqlalchemy.exc import IntegrityError
from app.infrastructure.storage.local import LocalStorage
from app.features.papers.models import Paper, PaperDocument
from datetime import datetime
from fastapi import BackgroundTasks
from app.features.papers.processing_service import process_document_background
from app.features.papers.enums import DocumentProcessingStatus
from app.infrastructure.rag.dependencies import get_rag_service
from app.infrastructure.summarization.service import (
    SummarizationService,
)
from app.features.papers.models import (
    Paper,
    PaperDocument,
    DocumentChunk,
)

from app.infrastructure.llm.service import LLMService


storage = LocalStorage()


#helper function for commit paper and for better error handling
def commit_paper(db: Session) -> None:
    try:
        db.commit()

    except IntegrityError as exc:
        db.rollback()

        if "papers_doi_key" in str(exc.orig):
            raise HTTPException(
                status_code=409,
                detail="A paper with this DOI already exists.",
            )

        raise


#create paper
def create_paper(
    data: PaperCreate,
    db: Session,
    owner_id: int,
) -> Paper:

    paper = Paper(
        title=data.title,
        abstract=data.abstract,
        authors=data.authors,
        publication_year=data.publication_year,
        journal=data.journal,
        doi=data.doi,
        category=data.category,
        pdf_url=str(data.pdf_url),
        owner_id=owner_id,
    )

    

    db.add(paper)

    commit_paper(db)

    db.refresh(paper)

    return paper



#get paper
def get_papers(
    db: Session,
    current_user,
    page: int,
    limit: int,
    category: str | None = None,
    publication_year: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
):
    offset = (page - 1) * limit

    total_query = (
        select(func.count())
        .select_from(Paper)
        .where(Paper.owner_id == current_user.id)
    )

    papers_query = (
        select(Paper)
        .where(Paper.owner_id == current_user.id)
    )

    # Category filter
    if category is not None:
        total_query = total_query.where(
            Paper.category == category
        )

        papers_query = papers_query.where(
            Paper.category == category
        )

    # Year filter
    if publication_year is not None:
        total_query = total_query.where(
            Paper.publication_year == publication_year
        )

        papers_query = papers_query.where(
            Paper.publication_year == publication_year
        )

    # Search
    if search is not None:
        search_pattern = f"%{search}%"

        search_condition = or_(
            Paper.title.ilike(search_pattern),
            Paper.authors.ilike(search_pattern),
        )

        total_query = total_query.where(search_condition)
        papers_query = papers_query.where(search_condition)

    # Sorting
    valid_sort_fields = {
        "title": Paper.title,
        "publication_year": Paper.publication_year,
        "created_at": Paper.created_at,
    }

    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort field"
        )

    sort_column = valid_sort_fields[sort_by]

    if order == "asc":
        papers_query = papers_query.order_by(
            sort_column.asc()
        )
    elif order == "desc":
        papers_query = papers_query.order_by(
            sort_column.desc()
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Order must be 'asc' or 'desc'"
        )

    # Count
    total = db.execute(total_query).scalar_one()

    # Pagination
    papers_query = (
        papers_query
        .offset(offset)
        .limit(limit)
    )

    result = db.execute(papers_query)

    papers = result.scalars().all()

    total_pages = (total + limit - 1) // limit

    return {
        "items": papers,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
    }


#get paper by id

def get_paper_by_id(
    paper_id: int,
    db: Session,
    current_user: User,
) -> Paper:

    paper = db.scalar(
        select(Paper).where(Paper.id == paper_id)
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found",
        )

    # Admins and reviewers can access any paper
    if current_user.role in {
        UserRole.ADMIN,
        UserRole.REVIEWER,
    }:
        return paper

    # Researchers can only access their own papers
    if paper.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this paper",
        )

    return paper



#Update Paper
def update_paper(
    paper_id: int,
    data: PaperUpdate,
    db: Session,
    current_user: User,
) -> Paper:

    paper = db.scalar(
        select(Paper).where(Paper.id == paper_id)
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found",
        )

    # Admin can update any paper
    if current_user.role == UserRole.ADMIN:
        pass

    # Researcher can update only their own paper
    elif current_user.role == UserRole.RESEARCHER:

        if paper.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to update this paper",
            )

    # Other roles are not allowed
    else:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update papers",
        )

    paper.title = data.title
    paper.abstract = data.abstract
    paper.authors = data.authors
    paper.publication_year = data.publication_year
    paper.journal = data.journal
    paper.doi = data.doi
    paper.category = data.category
    paper.pdf_url = str(data.pdf_url)
    
    commit_paper(db)

    db.refresh(paper)

    return paper



#Delete Paper
def delete_paper(
    paper_id: int,
    db: Session,
    current_user: User,
) -> None:

    paper = db.scalar(
        select(Paper).where(Paper.id == paper_id)
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found",
        )

    # Admin can delete any paper
    if current_user.role == UserRole.ADMIN:
        pass

    # Researcher can delete only their own paper
    elif current_user.role == UserRole.RESEARCHER:

        if paper.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to delete this paper",
            )

    # Other roles cannot delete
    else:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete papers",
        )

    db.delete(paper)
    db.commit()



#upload paper document function
async def upload_paper_document(
    db: Session,
    paper_id: int,
    file: UploadFile,
    current_user,
    background_tasks: BackgroundTasks,
):
    # 1. Find paper
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    # 2. Check existing document
    existing_document = (
        db.query(PaperDocument)
        .filter(PaperDocument.paper_id == paper_id)
        .first()
    )

    if existing_document:
        raise HTTPException(
            status_code=409,
            detail="Paper already has a document"
        )

    # 3. Validate PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 4. Save PDF
    storage_key, file_size = await storage.save(
        file,
        f"papers/{paper_id}"
    )

    # 5. Create document
    document = PaperDocument(
        paper_id=paper_id,
        file_name=file.filename,
        file_size=file_size,
        mime_type=file.content_type,
        storage_key=storage_key,
    )

    # 6. Save document
    db.add(document)
    db.commit()
    db.refresh(document)

    # 7. Schedule background processing
    background_tasks.add_task(
        process_document_background,
        document.id,
    )

    return document


#get document metadata
def get_paper_document(
    db: Session,
    paper_id: int,
    current_user,
):
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    document = (
        db.query(PaperDocument)
        .filter(PaperDocument.paper_id == paper_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


#function to get the actual pdf
def get_paper_document_file(
    db: Session,
    paper_id: int,
    current_user,
):
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    document = (
        db.query(PaperDocument)
        .filter(PaperDocument.paper_id == paper_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = storage.get_path(document.storage_key)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document file not found in storage"
        )

    return file_path, document


#delete actual  pdf
def delete_paper_document(
    db: Session,
    paper_id: int,
    current_user,
):
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    document = (
        db.query(PaperDocument)
        .filter(PaperDocument.paper_id == paper_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    storage.delete(document.storage_key)

    db.delete(document)
    db.commit()

    return {
        "message": "Paper document deleted successfully"
    }
    


#replace the existing document
async def replace_paper_document(
    db: Session,
    paper_id: int,
    file: UploadFile,
    current_user,
):
    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.owner_id == current_user.id
        )
        .first()
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    document = (
        db.query(PaperDocument)
        .filter(
            PaperDocument.paper_id == paper_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    old_storage_key = document.storage_key

    print("OLD STORAGE KEY:", old_storage_key)

    new_storage_key, new_file_size = await storage.save(
        file=file,
        folder=f"papers/{paper_id}"
    )

    print("NEW STORAGE KEY:", new_storage_key)

    document.file_name = file.filename
    document.file_size = new_file_size
    document.mime_type = file.content_type
    document.storage_key = new_storage_key
    document.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(document)

    print("DELETING OLD FILE:", old_storage_key)

    storage.delete(old_storage_key)
    



#Function for RAG Docuemnt Answers  Questions
def ask_paper(
    db: Session,
    paper_id: int,
    question: str,
    current_user,
):
    # 1. Find the paper and verify ownership
    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.owner_id == current_user.id,
        )
        .first()
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found",
        )

    # 2. Find the paper's document
    document = (
        db.query(PaperDocument)
        .filter(
            PaperDocument.paper_id == paper.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="No document found for this paper",
        )

    # 3. Make sure processing is completed
    if (
        document.processing_status
        != DocumentProcessingStatus.COMPLETED
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Document is not ready yet. "
                f"Current status: {document.processing_status}"
            ),
        )

    # 4. Get shared RAG service
    rag_service = get_rag_service()

    # 5. Ask the RAG pipeline
    rag_result = rag_service.ask(
        db=db,
        document_id=document.id,
        question=question,
    )

    # 6. Return structured response
    return {
        "paper_id": paper.id,
        "document_id": document.id,
        "question": question,
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
    }




#Summarize Paper
def summarize_paper(
    db: Session,
    paper_id: int,
    current_user,
):
    # 1. Find the paper and verify ownership
    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.owner_id == current_user.id,
        )
        .first()
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found",
        )

    # 2. Find the paper's document
    document = (
        db.query(PaperDocument)
        .filter(
            PaperDocument.paper_id == paper.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="No document found for this paper",
        )

    # 3. Make sure processing is completed
    if (
        document.processing_status
        != DocumentProcessingStatus.COMPLETED
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Document is not ready yet. "
                f"Current status: {document.processing_status}"
            ),
        )

    # 4. Get all document chunks in correct order
    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document.id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No processed chunks found for this document",
        )

    # 5. Combine chunk content
    document_text = "\n\n".join(
        chunk.content
        for chunk in chunks
    )

    # 6. Create summarization services
    llm_service = LLMService()

    summarization_service = SummarizationService(
        llm_service=llm_service,
    )

    # 7. Generate summary
    summary = summarization_service.summarize(
        document_text
    )

    # 8. Return result
    return {
        "paper_id": paper.id,
        "document_id": document.id,
        "summary": summary,
    }