from sqlalchemy.orm import Session
from sqlalchemy import select

from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate , PaperUpdate
from app.shared.enums.roles import UserRole
from app.features.users.models import User
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


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
):
    offset = (page - 1) * limit

    query = (
        select(Paper)
        .where(Paper.owner_id == current_user.id)
        .offset(offset)
        .limit(limit)
    )

    result = db.execute(query)

    return result.scalars().all()
    


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