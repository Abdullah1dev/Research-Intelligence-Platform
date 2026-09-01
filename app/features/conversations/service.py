from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.features.conversations.models import Conversation
from app.features.conversations.schemas import ConversationCreate

from app.features.papers.models import Paper


def create_conversation(
    db: Session,
    conversation_data: ConversationCreate,
    current_user,
) -> Conversation:

    # 1. Verify that the paper exists
    #    and belongs to the authenticated user
    paper = (
        db.query(Paper)
        .filter(
            Paper.id == conversation_data.paper_id,
            Paper.owner_id == current_user.id,
        )
        .first()
    )

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )

    # 2. Create conversation
    conversation = Conversation(
        title=conversation_data.title,
        user_id=current_user.id,
        paper_id=paper.id,
    )

    db.add(conversation)

    # 3. Save to database
    db.commit()

    # 4. Refresh object
    db.refresh(conversation)

    return conversation