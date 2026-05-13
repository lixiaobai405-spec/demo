from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chat import Conversation, Message
from app.schemas.chat import ChatRequest, ChatMessageOut, ConversationOut
from app.services.chat_service import stream_chat

router = APIRouter(prefix="/api/assessments", tags=["chat"])


@router.post("/{assessment_id}/chat")
async def chat(
    assessment_id: str,
    req: ChatRequest,
) -> StreamingResponse:
    return StreamingResponse(
        stream_chat(assessment_id, req.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/{assessment_id}/chat",
    response_model=ConversationOut,
    status_code=status.HTTP_200_OK,
)
def get_conversation(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> ConversationOut:
    conv = db.scalar(
        select(Conversation).where(Conversation.assessment_id == assessment_id)
    )
    if conv is None:
        return ConversationOut(
            id="",
            assessment_id=assessment_id,
            title="AI 商业顾问",
            messages=[],
        )

    msgs = db.scalars(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
    ).all()

    return ConversationOut(
        id=conv.id,
        assessment_id=conv.assessment_id,
        title=conv.title,
        messages=[
            ChatMessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in msgs
        ],
        created_at=conv.created_at,
    )


@router.delete(
    "/{assessment_id}/chat",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_conversation(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> None:
    conv = db.scalar(
        select(Conversation).where(Conversation.assessment_id == assessment_id)
    )
    if conv is not None:
        msgs = db.scalars(
            select(Message).where(Message.conversation_id == conv.id)
        ).all()
        for m in msgs:
            db.delete(m)
        db.delete(conv)
        db.commit()
