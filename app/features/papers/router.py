from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.infrastructure.database.config import get_db
from app.features.auth.dependencies import get_current_user
from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate, PaperResponse
from app.features.users.models import User
from app.features.papers.service import create_paper, get_papers


router = APIRouter(
    prefix="/papers",
    tags=["Papers"],
)


@router.post(
    "/",
    response_model=PaperResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: PaperCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_paper(
        data=data,
        db=db,
        owner_id=current_user.id,
    )
    
    

#get paper
@router.get(
    "/",
    response_model=list[PaperResponse],
)
def get_all_papers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_papers(
        db=db,
        current_user=current_user,
    )