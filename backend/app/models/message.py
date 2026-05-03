from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import uuid


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str = Field(regex="^(user|assistant|tool)$")  # Enum: user, assistant, tool
    content: str = Field(max_length=10000)
    tool_call_id: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
