from sqlalchemy.orm import Session
from sqlalchemy import select

from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate
from app.shared.enums.roles import UserRole
from app.features.users.models import User
from fastapi import HTTPException


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
        pdf_url=data.pdf_url,
        owner_id=owner_id,
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper



#get paper
def get_papers(
    db: Session,
    current_user: User,
) -> list[Paper]:

    if current_user.role in {
        UserRole.ADMIN,
        UserRole.REVIEWER,
    }:
        return db.scalars(
            select(Paper)
        ).all()

    return db.scalars(
        select(Paper).where(
            Paper.owner_id == current_user.id
        )
    ).all()
    


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