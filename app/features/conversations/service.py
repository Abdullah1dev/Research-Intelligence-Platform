from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.features.conversations.models import Conversation
from app.features.conversations.schemas import ConversationCreate

from app.features.papers.models import Paper
from langchain_core.messages import HumanMessage
from sqlalchemy import func

from app.infrastructure.agent.context import (
    ResearchAgentContext,
)




#Create Conversation
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


#Get all conversation
def get_conversations(
    db: Session,
    current_user,
) -> list[Conversation]:

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user.id,
        )
        .order_by(
            Conversation.updated_at.desc(),
        )
        .all()
    )

    return conversations



#Get specfic conversation
def get_conversation(
    db: Session,
    conversation_id: int,
    current_user,
) -> Conversation:

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation




#Delete conversation
def delete_conversation(
    db: Session,
    conversation_id: int,
    current_user,
) -> None:

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    db.delete(conversation)

    db.commit()
    


#Send message to agent
def send_message(
    db: Session,
    conversation_id: int,
    message: str,
    current_user,
    research_agent,
):

    # 1. Find conversation and verify ownership
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # 2. Create stable LangGraph thread ID
    thread_id = f"conversation_{conversation.id}"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # 3. Run research agent
    result = research_agent.invoke(
        {
            "messages": [
                HumanMessage(content=message)
            ],
            "conversation_id": conversation.id,
            "user_id": current_user.id,
            "paper_id": conversation.paper_id,
        },
        config=config,
        context=ResearchAgentContext(
            db=db
        ),
    )

    # 4. Get final AI message
    ai_message = result["messages"][-1]

    # 5. Update conversation timestamp
    conversation.updated_at = func.now()

    db.commit()
    db.refresh(conversation)

    # 6. Return response
    return {
        "conversation_id": conversation.id,
        "paper_id": conversation.paper_id,
        "answer": ai_message.content,
    }