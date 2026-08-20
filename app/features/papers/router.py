from fastapi import APIRouter, Depends, status , Query , UploadFile , File 
from sqlalchemy.orm import Session

from app.infrastructure.database.config import get_db
from app.features.auth.dependencies import get_current_user
from app.features.papers.models import Paper
from app.features.papers.schemas import PaperCreate, PaperResponse , PaperUpdate , PaginatedPaperResponse
from app.features.users.models import User
from app.features.papers.service import create_paper, get_papers , get_paper_by_id , update_paper ,  delete_paper 
from app.features.papers.enums import PaperSortField, SortOrder
from app.features.papers.schemas import PaperDocumentResponse
from app.features.papers.service import upload_paper_document

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
@router.get("/", response_model=PaginatedPaperResponse)
def get_all_papers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    category: str | None = Query(None),
    publication_year: int | None = Query(None),
    search: str | None = Query(None),

    sort_by: PaperSortField = Query(
        PaperSortField.CREATED_AT,
        description="Field used to sort papers."
    ),

    order: SortOrder = Query(
        SortOrder.DESC,
        description="Sorting direction."
    ),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_papers(
        db=db,
        current_user=current_user,
        page=page,
        limit=limit,
        category=category,
        publication_year=publication_year,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    


#get paper by single id

@router.get(
    "/{paper_id}",
    response_model=PaperResponse,
)
def get_single_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_paper_by_id(
        paper_id=paper_id,
        db=db,
        current_user=current_user,
    )
    
    

@router.put(
    "/{paper_id}",
    response_model=PaperResponse,
)
def update_single_paper(
    paper_id: int,
    data: PaperUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_paper(
        paper_id=paper_id,
        data=data,
        db=db,
        current_user=current_user,
    )
    
    


#delete paper
@router.delete(
    "/{paper_id}",
    status_code=204,
)
def delete_single_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_paper(
        paper_id=paper_id,
        db=db,
        current_user=current_user,
    )
    

#upload paper document
@router.post(
    "/{paper_id}/document",
    response_model=PaperDocumentResponse,
    status_code=201,
)
async def upload_document(
    paper_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await upload_paper_document(
        db=db,
        paper_id=paper_id,
        file=file,
    )