from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from typing import Optional, Tuple
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.utils.sanitization import sanitizer


class TaskService:
    """Service for task CRUD operations"""

    @staticmethod
    async def create_task(
        session: AsyncSession,
        user_id: int,
        task_data: TaskCreate
    ) -> Task:
        """Create a new task for a user"""
        # Validate title is not empty after stripping
        title = task_data.title.strip()
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty or only whitespace"
            )

        # Sanitize title to prevent XSS
        title = sanitizer.sanitize_string(title)

        # Validate and strip description if provided
        description = None
        if task_data.description:
            description = task_data.description.strip()
            if not description:
                description = None  # Convert empty string to None
            else:
                # Sanitize description to prevent XSS
                description = sanitizer.sanitize_string(description)

        # Sanitize tags if provided
        tags = sanitizer.sanitize_list(task_data.tags) if task_data.tags else None

        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=task_data.priority,
            tags=tags,
            due_date=task_data.due_date,
            is_recurring=task_data.is_recurring,
            recurrence_pattern=task_data.recurrence_pattern,
            recurrence_interval=task_data.recurrence_interval,
            recurrence_end_date=task_data.recurrence_end_date,
            reminder_enabled=task_data.reminder_enabled,
            reminder_minutes_before=task_data.reminder_minutes_before,
        )

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        return new_task

    @staticmethod
    async def get_user_tasks(
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        completed: Optional[bool] = None
    ) -> Tuple[list[Task], int]:
        """Get all tasks for a user with pagination and filtering"""
        # Build base query
        query = select(Task).where(Task.user_id == user_id)

        # Apply completed filter if provided
        if completed is not None:
            query = query.where(Task.completed == completed)

        # Get total count
        count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)
        if completed is not None:
            count_query = count_query.where(Task.completed == completed)

        total_result = await session.execute(count_query)
        total = total_result.scalar()

        # Apply ordering and pagination
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)

        result = await session.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    @staticmethod
    async def get_task_by_id(
        session: AsyncSession,
        task_id: int,
        user_id: int
    ) -> Optional[Task]:
        """Get a single task by ID with ownership check"""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_task(
        session: AsyncSession,
        task_id: int,
        user_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task with ownership check"""
        task = await TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return None

        # Update only provided fields
        if task_data.title is not None:
            title = task_data.title.strip()
            if not title:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Title cannot be empty or only whitespace"
                )
            # Sanitize title to prevent XSS
            task.title = sanitizer.sanitize_string(title)

        if task_data.description is not None:
            description = task_data.description.strip()
            # Sanitize description to prevent XSS
            task.description = sanitizer.sanitize_string(description) if description else None

        if task_data.completed is not None:
            task.completed = task_data.completed

        if task_data.priority is not None:
            task.priority = task_data.priority

        if task_data.tags is not None:
            # Sanitize tags to prevent XSS
            task.tags = sanitizer.sanitize_list(task_data.tags)

        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        if task_data.is_recurring is not None:
            task.is_recurring = task_data.is_recurring

        if task_data.recurrence_pattern is not None:
            task.recurrence_pattern = task_data.recurrence_pattern

        if task_data.recurrence_interval is not None:
            task.recurrence_interval = task_data.recurrence_interval

        if task_data.recurrence_end_date is not None:
            task.recurrence_end_date = task_data.recurrence_end_date

        if task_data.reminder_enabled is not None:
            task.reminder_enabled = task_data.reminder_enabled

        if task_data.reminder_minutes_before is not None:
            task.reminder_minutes_before = task_data.reminder_minutes_before

        # Manually update updated_at timestamp
        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def delete_task(
        session: AsyncSession,
        task_id: int,
        user_id: int
    ) -> bool:
        """Delete a task with ownership check"""
        task = await TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return False

        await session.delete(task)
        await session.commit()

        return True
