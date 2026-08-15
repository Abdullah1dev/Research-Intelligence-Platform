from sqlalchemy.orm import Session

from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate


def create_paper(
    data: PaperCreate,
    db: Session,
    owner_id: int,
) -> Paper:

    paper = Paper(
        title=data.title,
        abstract=data.abstract,
        content=data.content,
        owner_id=owner_id,
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper