"""
MCP tool Pydantic schemas for input validation.

[Task]: T012
[From]: speckit.specify, contracts/mcp-tools.md

Defines input models for all 5 MCP tools with Pydantic validation.
user_id is injected by the agent service from JWT, never from user input.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    title: str = Field(min_length=1, max_length=200, description="Task title extracted from user message")
    description: str = Field(default="", max_length=2000, description="Optional task description")


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    status: str = Field(default="all", description="Filter by status: all, pending, completed")


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    task_id: int = Field(description="ID of the task to mark complete")


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    task_id: int = Field(description="ID of the task to update")
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(default=None, max_length=2000, description="New task description")


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    task_id: int = Field(description="ID of the task to delete")
