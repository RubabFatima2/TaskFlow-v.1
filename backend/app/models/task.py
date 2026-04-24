from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index, ForeignKey, Column, Integer, JSON
from datetime import datetime, date
from typing import Optional, List


class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        Index('ix_tasks_user_completed_created', 'user_id', 'completed', 'created_at'),
        Index('ix_tasks_priority', 'priority'),
        Index('ix_tasks_due_date', 'due_date'),
        Index('ix_tasks_recurring', 'is_recurring'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True))
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="medium", max_length=10)  # low, medium, high
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(default=None)  # Changed to datetime to include time
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=50)  # daily, weekly, monthly, yearly
    recurrence_interval: Optional[int] = Field(default=1)  # Every X days/weeks/months
    recurrence_end_date: Optional[date] = Field(default=None)
    parent_task_id: Optional[int] = Field(default=None)  # For tracking recurring task instances
    reminder_enabled: bool = Field(default=False)
    reminder_minutes_before: Optional[int] = Field(default=None)  # Minutes before due date
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
