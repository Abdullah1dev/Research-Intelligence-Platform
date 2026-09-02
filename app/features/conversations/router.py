from typing import List

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
     Request,
)


from sqlalchemy.orm import Session

from app.infrastructure.database.config import get_db

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

from app.features.conversations.schemas import (
    ConversationMessageRequest,
    ConversationMessageResponse,
)

from app.features.conversations.service import (
    send_message,
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



# Get a specific conversation
@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return get_conversation(
        db=db,
        conversation_id=conversation_id,
        current_user=current_user,
    )



# Delete conversation
@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    delete_conversation(
        db=db,
        conversation_id=conversation_id,
        current_user=current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
    

@router.post(
    "/{conversation_id}/messages",
    response_model=ConversationMessageResponse,
)
def send_conversation_message(

    conversation_id: int,

    request_body: ConversationMessageRequest,

    request: Request,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user),

):

    # Get the already initialized Research Agent
    research_agent = (
        request.app.state.research_agent
    )

    return send_message(

        db=db,

        conversation_id=conversation_id,

        message=request_body.message,

        current_user=current_user,

        research_agent=research_agent,

    )