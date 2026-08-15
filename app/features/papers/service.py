from sqlalchemy.orm import Session
from sqlalchemy import select

from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate
from app.shared.enums.roles import UserRole
from app.features.users.models import User


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