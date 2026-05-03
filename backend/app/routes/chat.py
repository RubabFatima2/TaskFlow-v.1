"""
Chat endpoint for AI-powered task management.

[Task]: T015, T019, T020, T023, T026, T028, T038, T039, T058
[From]: speckit.specify, contracts/chat-api.yaml

POST /api/v1/chat — Send message to AI chatbot
GET /api/v1/conversations — List user's conversations

All endpoints require JWT authentication via cookie.
user_id is always extracted from JWT token.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.services.agent_service import process_message
from app.utils.dependencies import get_db_session, get_current_user
from app.middleware.rate_limit import chat_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


# ─── Request/Response Models ────────────────────────────────


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    conversation_id: Optional[str] = Field(
        default=None,
        description="UUID of existing conversation. If omitted, new conversation created.",
    )
    message: str = Field(
        min_length=1,
        max_length=5000,
        description="User's message text",
    )


class ToolCallResponse(BaseModel):
    """Tool call details in chat response."""
    tool_name: str
    input: dict
    success: bool


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    conversation_id: str
    response: str
    tool_calls: List[ToolCallResponse] = []
    message_id: Optional[str] = None
    timestamp: Optional[str] = None


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""
    id: str
    created_at: str
    updated_at: str


class ConversationListResponse(BaseModel):
    """Response for listing conversations."""
    conversations: List[ConversationSummary]
    count: int


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    error_code: str
    status: int


class MessageResponse(BaseModel):
    """Message in a conversation."""
    id: str
    conversation_id: str
    role: str
    content: str
    tool_call_id: Optional[str] = None
    created_at: str


class MessageListResponse(BaseModel):
    """Response for listing messages in a conversation."""
    messages: List[MessageResponse]
    count: int


# ─── Endpoints ───────────────────────────────────────────────


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(chat_rate_limit),
):
    """
    Send a message to the AI chatbot.

    [Task]: T015, T019, T020, T023, T028

    - Creates new conversation if conversation_id is None
    - Verifies conversation ownership if conversation_id provided
    - Validates conversation_id UUID format
    - Saves user + assistant messages to database
    - Returns AI response with tool call details
    """
    user_id = current_user.id
    conversation_id = request.conversation_id

    # ── Validate conversation_id format ─────────────────
    # [Task]: T058
    if conversation_id is not None:
        try:
            uuid.UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation_id format. Must be a valid UUID.",
            )

    # ── Get or create conversation ──────────────────────
    if conversation_id:
        # [Task]: T028 — Verify conversation ownership
        stmt = select(Conversation).where(
            Conversation.id == conversation_id
        )
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation",
            )
    else:
        # [Task]: T019 — Create new conversation
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(conversation)
        await session.flush()  # Get the ID without committing
        conversation_id = conversation.id

    # ── Process message through agent ───────────────────
    try:
        agent_result = await process_message(
            session=session,
            user_id=user_id,
            message=request.message,
            conversation_id=conversation_id ,
        )
    except Exception as e:
        logger.error(f"Agent processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again.",
        )

    # Check for error code from agent service
    # [Issue 5] Map error codes to proper HTTP status codes
    error_code = agent_result.get("error_code")
    if error_code == "RATE_LIMITED":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=agent_result["response"],
        )
    elif error_code == "TIMEOUT":
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=agent_result["response"],
        )
    elif error_code == "AI_SERVICE_ERROR":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=agent_result["response"],
        )

    # ── Save user message ───────────────────────────────
    # [Task]: T020
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    user_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=request.message,
        created_at=now,
    )
    session.add(user_message)

    # ── Save tool messages ──────────────────────────────
    # [Fix]: Context memory leak - persist tool results
    for tool_msg in agent_result.get("tool_messages", []):
        tool_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            user_id=user_id,
            role="tool",
            content=tool_msg["content"],
            tool_call_id=tool_msg["tool_call_id"],
            created_at=now,
        )
        session.add(tool_message)

    # ── Save assistant message ──────────────────────────
    assistant_message_id = str(uuid.uuid4())
    assistant_message = Message(
        id=assistant_message_id,
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=agent_result["response"],
        created_at=now,
    )
    session.add(assistant_message)

    # ── Update conversation timestamp ───────────────────
    # [Task]: T038 [US6]
    conversation.updated_at = now

    await session.commit()

    # ── Build response ──────────────────────────────────
    tool_calls = [
        ToolCallResponse(
            tool_name=tc.get("tool_name", "unknown"),
            input=tc.get("input", {}),
            success=tc.get("success", True),
        )
        for tc in agent_result.get("tool_calls", [])
    ]

    return ChatResponse(
        conversation_id=conversation_id,
        response=agent_result["response"],
        tool_calls=tool_calls,
        message_id=assistant_message_id,
        timestamp=now.isoformat() + "Z",
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    List user's conversations ordered by most recent activity.

    [Task]: T039 [US6]
    """
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
    )
    result = await session.execute(stmt)
    conversations = result.scalars().all()

    summaries = [
        ConversationSummary(
            id=c.id,
            created_at=c.created_at.isoformat() + "Z" if c.created_at else "",
            updated_at=c.updated_at.isoformat() + "Z" if c.updated_at else "",
        )
        for c in conversations
    ]

    return ConversationListResponse(
        conversations=summaries,
        count=len(summaries),
    )


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get all messages in a conversation.

    [Task]: T059 [Issue 3]
    """
    try:
        uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation_id format. Must be a valid UUID.",
        )

    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await session.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation",
        )

    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()

    message_responses = [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            tool_call_id=m.tool_call_id,
            created_at=m.created_at.isoformat() + "Z" if m.created_at else "",
        )
        for m in messages
    ]

    return MessageListResponse(
        messages=message_responses,
        count=len(message_responses),
    )

# conversation_id=conversation_id if request.conversation_id else None