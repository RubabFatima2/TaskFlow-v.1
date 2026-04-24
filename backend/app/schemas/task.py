from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TaskCreate(BaseModel):
    """Request schema for creating a task"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = Field(default=None)
    due_date: Optional[datetime] = None
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly|yearly)$")
    recurrence_interval: Optional[int] = Field(default=1, ge=1)
    recurrence_end_date: Optional[date] = None
    reminder_enabled: bool = Field(default=False)
    reminder_minutes_before: Optional[int] = Field(default=None, ge=0)


class TaskUpdate(BaseModel):
    """Request schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10000)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly|yearly)$")
    recurrence_interval: Optional[int] = Field(default=None, ge=1)
    recurrence_end_date: Optional[date] = None
    reminder_enabled: Optional[bool] = None
    reminder_minutes_before: Optional[int] = Field(default=None, ge=0)


class TaskResponse(BaseModel):
    """Response schema for task data"""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: Optional[List[str]]
    due_date: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    recurrence_interval: Optional[int]
    recurrence_end_date: Optional[date]
    parent_task_id: Optional[int]
    reminder_enabled: bool
    reminder_minutes_before: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response schema for list of tasks"""
    tasks: list[TaskResponse]
    total: int
