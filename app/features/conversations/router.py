from typing import List

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.infrastructure.database.dependencies import get_db

from app.features.auth.dependencies import get_current_user

from app.features.conversations.schemas import (
    ConversationCreate,
    ConversationResponse,
)

from app.features.conversations.service import (
    create_conversation,
    get_conversations,
    get_conversation,
    delete_conversation,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


# Create conversation
@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation_endpoint(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return create_conversation(
        db=db,
        conversation_data=conversation_data,
        current_user=current_user,
    )
    



# Get all conversations
@router.get(
    "/",
    response_model=list[ConversationResponse],
)
def get_conversations_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return get_conversations(
        db=db,
        current_user=current_user,
    )
