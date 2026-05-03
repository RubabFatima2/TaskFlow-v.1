"""
MCP tool implementations for AI chatbot task management.

[Task]: T013, T017, T024, T029, T033, T036
[From]: speckit.specify, contracts/mcp-tools.md

All 5 async functions that operate on the existing Task model.
user_id is always injected by the agent service from JWT token.
All database queries filter by user_id for data isolation.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.task import Task
from app.utils.sanitization import sanitizer

logger = logging.getLogger(__name__)


async def add_task(
    session: AsyncSession,
    user_id: int,
    title: str,
    description: str = ""
) -> dict:
    """
    Create a new task for the authenticated user.

    [Task]: T017 [US1]
    """
    try:
        # Sanitize inputs
        clean_title = sanitizer.sanitize_string(title.strip())
        if not clean_title:
            return {"success": False, "error": "Title cannot be empty"}

        clean_description = None
        if description:
            clean_description = sanitizer.sanitize_string(description.strip())

        task = Task(
            user_id=user_id,
            title=clean_title,
            description=clean_description,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        logger.info(f"Task created: id={task.id}, user_id={user_id}, title={clean_title}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            }
        }
    except Exception as e:
        logger.error(f"add_task failed: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to create task: {str(e)}"}


async def list_tasks(
    session: AsyncSession,
    user_id: int,
    status: str = "all"
) -> dict:
    """
    List tasks for the authenticated user with optional status filter.

    [Task]: T024 [US2]
    """
    try:
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        # "all" means no filter

        query = query.order_by(Task.created_at.desc())
        result = await session.execute(query)
        tasks = result.scalars().all()

        tasks_data = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description or "",
                "completed": t.completed,
                "priority": t.priority,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in tasks
        ]

        logger.info(f"list_tasks: user_id={user_id}, status={status}, count={len(tasks_data)}")

        return {
            "success": True,
            "tasks": tasks_data,
            "count": len(tasks_data)
        }
    except Exception as e:
        logger.error(f"list_tasks failed: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to list tasks: {str(e)}"}


async def complete_task(
    session: AsyncSession,
    user_id: int,
    task_id: int
) -> dict:
    """
    Mark a task as completed.

    [Task]: T029 [US3]
    """
    try:
        stmt = select(Task).where(Task.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return {"success": False, "error": "Task not found"}

        if task.user_id != user_id:
            return {"success": False, "error": "Task does not belong to user"}

        task.completed = True
        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await session.commit()
        await session.refresh(task)

        logger.info(f"Task completed: id={task.id}, user_id={user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "completed": True,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }
        }
    except Exception as e:
        logger.error(f"complete_task failed: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to complete task: {str(e)}"}


async def update_task(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Update a task's title and/or description.

    [Task]: T033, T035 [US4]
    """
    try:
        if title is None and description is None:
            return {"success": False, "error": "At least one of title or description must be provided"}

        stmt = select(Task).where(Task.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return {"success": False, "error": "Task not found"}

        if task.user_id != user_id:
            return {"success": False, "error": "Task does not belong to user"}

        if title is not None:
            clean_title = sanitizer.sanitize_string(title.strip())
            if not clean_title:
                return {"success": False, "error": "Title cannot be empty"}
            task.title = clean_title

        if description is not None:
            task.description = sanitizer.sanitize_string(description.strip()) if description.strip() else None

        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await session.commit()
        await session.refresh(task)

        logger.info(f"Task updated: id={task.id}, user_id={user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }
        }
    except Exception as e:
        logger.error(f"update_task failed: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to update task: {str(e)}"}


async def delete_task(
    session: AsyncSession,
    user_id: int,
    task_id: int
) -> dict:
    """
    Permanently delete a task.

    [Task]: T036 [US5]
    """
    try:
        stmt = select(Task).where(Task.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return {"success": False, "error": "Task not found"}

        if task.user_id != user_id:
            return {"success": False, "error": "Task does not belong to user"}

        task_title = task.title
        await session.delete(task)
        await session.commit()

        logger.info(f"Task deleted: id={task_id}, user_id={user_id}, title={task_title}")

        return {
            "success": True,
            "message": f"Task '{task_title}' deleted successfully"
        }
    except Exception as e:
        logger.error(f"delete_task failed: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to delete task: {str(e)}"}
