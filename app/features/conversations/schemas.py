from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ConversationCreate(BaseModel):

    paper_id: int = Field(
        ...,
        description="ID of the paper for this conversation",
    )

    title: str | None = Field(
        default=None,
        max_length=255,
        description="Optional title for the conversation",
    )


class ConversationResponse(BaseModel):

    id: int

    title: str | None

    user_id: int

    paper_id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
    

class ConversationChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        description="Message sent by the user",
    )



class ConversationChatResponse(BaseModel):

    conversation_id: int

    answer: str