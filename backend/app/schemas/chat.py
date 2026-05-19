from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    current_page: str | None = None


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime | None = None


class ConversationOut(BaseModel):
    id: str
    assessment_id: str
    title: str
    messages: list[ChatMessageOut] = Field(default_factory=list)
    created_at: datetime | None = None
