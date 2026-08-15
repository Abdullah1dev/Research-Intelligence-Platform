from sqlalchemy.orm import Session
from sqlalchemy import select

from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate

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
) -> list[Paper]:

    result = db.scalars(
        select(Paper)
    ).all()

    return result