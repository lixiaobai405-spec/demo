from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chat import Conversation, Message
from app.schemas.chat import ChatRequest, ChatMessageOut, ConversationOut
from app.services.chat_service import stream_chat
from app.services.intake_service import IntakeService

router = APIRouter(prefix="/api/assessments", tags=["chat"])


@router.post("/{assessment_id}/chat")
async def chat(
    assessment_id: str,
    request: Request,
) -> StreamingResponse:
    content_type = request.headers.get("content-type", "")
    message = ""
    attachments: list[dict[str, object]] = []

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        message = str(form.get("message", "") or "").strip()
        files = [item for item in form.getlist("files") if isinstance(item, UploadFile)]
        intake_service = IntakeService()
        for upload in files:
            source_file, raw_content, warnings = await intake_service.extract_upload_file(
                upload
            )
            attachments.append(
                {
                    "name": source_file.name,
                    "kind": source_file.kind,
                    "size_bytes": source_file.size_bytes,
                    "warnings": warnings,
                    "content": raw_content,
                }
            )
    else:
        req = ChatRequest.model_validate(await request.json())
        message = req.message.strip()

    if not message and not attachments:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message or files are required.",
        )

    return StreamingResponse(
        stream_chat(assessment_id, message, attachments=attachments),
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
