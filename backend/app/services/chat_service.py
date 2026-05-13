import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.assessment import Assessment
from app.models.canvas_diagnosis import CanvasDiagnosis
from app.models.direction_selection import DirectionSelection
from app.models.endgame_analysis import EndgameAnalysis
from app.models.chat import Conversation, Message

logger = logging.getLogger(__name__)


def _build_context(assessment_id: str, db: Session) -> str:
    """Build AI context from all generated assessment results."""
    parts: list[str] = []

    # Assessment basic info
    assessment = db.scalar(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    if assessment:
        parts.append(f"## 企业基础信息")
        parts.append(f"- 公司名称：{assessment.company_name}")
        parts.append(f"- 行业：{assessment.industry}")
        parts.append(f"- 规模：{assessment.company_size}")
        parts.append(f"- 地区：{assessment.region}")
        parts.append(f"- 收入范围：{assessment.annual_revenue_range}")
        parts.append(f"- 核心产品：{assessment.core_products}")
        parts.append(f"- 目标客户：{assessment.target_customers}")
        parts.append(f"- 当前挑战：{assessment.current_challenges}")
        parts.append(f"- AI 目标：{assessment.ai_goals}")
        parts.append(f"- 可用数据：{assessment.available_data}")
        if assessment.notes:
            parts.append(f"- 备注：{assessment.notes}")

    # Canvas diagnosis
    canvas = db.scalar(
        select(CanvasDiagnosis).where(CanvasDiagnosis.assessment_id == assessment_id)
    )
    if canvas:
        parts.append(f"\n## 商业画布 9 格诊断")
        parts.append(f"总分：{canvas.overall_score}")
        if canvas.canvas_json:
            try:
                canvas_data = json.loads(canvas.canvas_json)
                if isinstance(canvas_data, dict):
                    summary = canvas_data.get("overall_summary", "")
                    if summary:
                        parts.append(f"总结：{summary}")
            except (json.JSONDecodeError, TypeError):
                pass

    # Direction selection
    direction = db.scalar(
        select(DirectionSelection).where(
            DirectionSelection.assessment_id == assessment_id
        )
    )
    if direction and direction.directions_json:
        try:
            dirs = json.loads(direction.directions_json)
            if isinstance(dirs, list) and dirs:
                parts.append(f"\n## 已选创新方向（{len(dirs)} 个）")
                for d in dirs:
                    if isinstance(d, dict):
                        parts.append(
                            f"- {d.get('title', '')}: {d.get('description', '')}"
                        )
        except (json.JSONDecodeError, TypeError):
            pass

    # Endgame analysis
    endgame = db.scalar(
        select(EndgameAnalysis).where(
            EndgameAnalysis.assessment_id == assessment_id
        )
    )
    if endgame and endgame.overall_narrative:
        parts.append(f"\n## 商业终局设计")
        parts.append(endgame.overall_narrative)

    return "\n".join(parts)


SYSTEM_PROMPT_TEMPLATE = """你是一个 AI 商业创新顾问，专门帮助企业分析商业模式、制定 AI 转型策略。

## 当前企业评估数据

{context}

## 对话要求

- 基于上面的评估数据回答用户问题
- 如果数据不足以回答某个问题，诚实说明并建议先生成对应模块
- 回答简洁专业，聚焦可落地的商业建议
- 优先引用评估数据中的具体信息
- 用户可能在不同页面（画布、方向延展、终局设计、结果仪表盘）与你对话
- 当用户在新页面生成新结果后，你会自动获得更新后的上下文

请用中文回答。"""


def build_system_prompt(assessment_id: str, db: Session) -> str:
    context = _build_context(assessment_id, db)
    return SYSTEM_PROMPT_TEMPLATE.format(context=context)


async def stream_chat(assessment_id: str, user_message: str):
    """Stream AI chat response via SSE using DeepSeek API.

    Yields SSE-formatted strings:
        data: {"token": "..."}
        data: {"done": true, "message_id": "..."}
        data: {"error": "..."}
    """
    db = SessionLocal()
    conversation = None
    assistant_content = ""

    try:
        # Load or create conversation
        conversation = db.scalar(
            select(Conversation).where(
                Conversation.assessment_id == assessment_id
            )
        )
        if conversation is None:
            conversation = Conversation(assessment_id=assessment_id)
            db.add(conversation)
            db.flush()
            db.refresh(conversation)

        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=user_message,
        )
        db.add(user_msg)
        db.commit()

        # Build system prompt with latest context
        system_prompt = build_system_prompt(assessment_id, db)

        # Load recent history (last 20 messages)
        history = db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(20)
        ).all()
        history.reverse()

        # Build messages for DeepSeek
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        # Call DeepSeek streaming
        if settings.llm_mode != "live" or not settings.openai_api_key:
            yield f"data: {json.dumps({'error': 'LLM 未启用，请在 mykey.py 中设置 llm_mode=live'})}\n\n"
            return

        from openai import OpenAI

        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

        stream = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                assistant_content += delta.content
                yield f"data: {json.dumps({'token': delta.content})}\n\n"

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_content,
        )
        db.add(assistant_msg)
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()

        yield f"data: {json.dumps({'done': True, 'message_id': assistant_msg.id})}\n\n"

    except Exception as exc:
        logger.warning("Chat stream error for assessment %s: %s", assessment_id, exc)
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
    finally:
        db.close()
