import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.models.user import User
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException


@pytest.mark.asyncio
class TestTaskService:
    """Test task service operations"""

    async def test_create_task_success(self, test_db, test_user, client):
        """Test successful task creation"""
        from app.database import get_session

        async for session in get_session():
            task_data = TaskCreate(
                title="Test Task",
                description="Test Description"
            )

            task = await TaskService.create_task(session, test_user["id"], task_data)

            assert task is not None
            assert task.id is not None
            assert task.user_id == test_user["id"]
            assert task.title == "Test Task"
            assert task.description == "Test Description"
            assert task.completed is False
            assert task.created_at is not None
            assert task.updated_at is not None
            break

    async def test_create_task_strips_whitespace(self, test_db, test_user, client):
        """Test that task title whitespace is stripped"""
        from app.database import get_session

        async for session in get_session():
            task_data = TaskCreate(
                title="  Whitespace Task  ",
                description="Test"
            )

            task = await TaskService.create_task(session, test_user["id"], task_data)

            assert task.title == "Whitespace Task"
            break

    async def test_create_task_empty_title_raises_error(self, test_db, test_user, client):
        """Test that empty title raises validation error"""
        from app.database import get_session

        async for session in get_session():
            task_data = TaskCreate(
                title="   ",  # Only whitespace
                description="Test"
            )

            with pytest.raises(HTTPException) as exc_info:
                await TaskService.create_task(session, test_user["id"], task_data)

            assert exc_info.value.status_code == 400
            assert "empty" in exc_info.value.detail.lower()
            break

    async def test_create_task_without_description(self, test_db, test_user, client):
        """Test creating task without description"""
        from app.database import get_session

        async for session in get_session():
            task_data = TaskCreate(title="No Description Task")

            task = await TaskService.create_task(session, test_user["id"], task_data)

            assert task.title == "No Description Task"
            assert task.description is None
            break

    async def test_get_user_tasks(self, test_db, test_user, client):
        """Test getting all tasks for a user"""
        from app.database import get_session

        async for session in get_session():
            # Create multiple tasks
            task1 = TaskCreate(title="Task 1", description="First")
            task2 = TaskCreate(title="Task 2", description="Second")
            task3 = TaskCreate(title="Task 3", description="Third")

            await TaskService.create_task(session, test_user["id"], task1)
            await TaskService.create_task(session, test_user["id"], task2)
            await TaskService.create_task(session, test_user["id"], task3)

            # Get all tasks
            tasks = await TaskService.get_user_tasks(session, test_user["id"])

            assert len(tasks) == 3
            assert all(task.user_id == test_user["id"] for task in tasks)
            break

    async def test_get_user_tasks_ordered_by_created_at(self, test_db, test_user, client):
        """Test that tasks are ordered by created_at descending"""
        from app.database import get_session
        import asyncio

        async for session in get_session():
            # Create tasks with slight delay
            task1 = TaskCreate(title="First Task")
            await TaskService.create_task(session, test_user["id"], task1)
            await asyncio.sleep(0.1)

            task2 = TaskCreate(title="Second Task")
            await TaskService.create_task(session, test_user["id"], task2)
            await asyncio.sleep(0.1)

            task3 = TaskCreate(title="Third Task")
            await TaskService.create_task(session, test_user["id"], task3)

            # Get all tasks
            tasks = await TaskService.get_user_tasks(session, test_user["id"])

            # Should be in reverse order (newest first)
            assert tasks[0].title == "Third Task"
            assert tasks[1].title == "Second Task"
            assert tasks[2].title == "First Task"
            break

    async def test_get_task_by_id_success(self, test_db, test_user, client):
        """Test getting task by ID with ownership check"""
        from app.database import get_session

        async for session in get_session():
            # Create task
            task_data = TaskCreate(title="Get By ID Task")
            created_task = await TaskService.create_task(session, test_user["id"], task_data)

            # Get task by ID
            task = await TaskService.get_task_by_id(session, created_task.id, test_user["id"])

            assert task is not None
            assert task.id == created_task.id
            assert task.title == "Get By ID Task"
            break

    async def test_get_task_by_id_wrong_user_returns_none(self, test_db, test_user, client):
        """Test that getting task with wrong user_id returns None"""
        from app.database import get_session

        async for session in get_session():
            # Create task
            task_data = TaskCreate(title="Ownership Test Task")
            created_task = await TaskService.create_task(session, test_user["id"], task_data)

            # Try to get with different user_id
            task = await TaskService.get_task_by_id(session, created_task.id, 99999)

            assert task is None
            break

    async def test_update_task_completed_status(self, test_db, test_user, client):
        """Test updating task completed status"""
        from app.database import get_session

        async for session in get_session():
            # Create task
            task_data = TaskCreate(title="Complete Me")
            created_task = await TaskService.create_task(session, test_user["id"], task_data)
            assert created_task.completed is False

            # Mark as completed
            update_data = TaskUpdate(completed=True)
            updated_task = await TaskService.update_task(
                session, created_task.id, test_user["id"], update_data
            )

            assert updated_task.completed is True
            break

    async def test_update_task_empty_title_raises_error(self, test_db, test_user, client):
        """Test that updating to empty title raises error"""
        from app.database import get_session

        async for session in get_session():
            # Create task
            task_data = TaskCreate(title="Valid Title")
            created_task = await TaskService.create_task(session, test_user["id"], task_data)

            # Try to update with empty title
            update_data = TaskUpdate(title="   ")

            with pytest.raises(HTTPException) as exc_info:
                await TaskService.update_task(
                    session, created_task.id, test_user["id"], update_data
                )

            assert exc_info.value.status_code == 400
            break

    async def test_update_task_wrong_user_returns_none(self, test_db, test_user, client):
        """Test that updating task with wrong user_id returns None"""
        from app.database import get_session

        async for session in get_session():
            # Create task
            task_data = TaskCreate(title="Ownership Test")
            created_task = await TaskService.create_task(session, test_user["id"], task_data)

            # Try to update with different user_id
            update_data = TaskUpdate(title="Hacked Title")
            updated_task = await TaskService.update_task(
                session, created_task.id, 99999, update_data
            )

            assert updated_task is None
            break

    async def test_delete_task_success(self, test_db, test_user, client):
        """Test successful task deletion"""
        from app.database import get_session

        async for session in get_session():
            # Create task
            task_data = TaskCreate(title="Delete Me")
            created_task = await TaskService.create_task(session, test_user["id"], task_data)

            # Delete task
            deleted = await TaskService.delete_task(session, created_task.id, test_user["id"])

            assert deleted is True

            # Verify task is deleted
            task = await TaskService.get_task_by_id(session, created_task.id, test_user["id"])
            assert task is None
            break

    async def test_delete_task_wrong_user_returns_false(self, test_db, test_user, client):
        """Test that deleting task with wrong user_id returns False"""
        from app.database import get_session

        async for session in get_session():
            # Create task
            task_data = TaskCreate(title="Protected Task")
            created_task = await TaskService.create_task(session, test_user["id"], task_data)

            # Try to delete with different user_id
            deleted = await TaskService.delete_task(session, created_task.id, 99999)

            assert deleted is False

            # Verify task still exists
            task = await TaskService.get_task_by_id(session, created_task.id, test_user["id"])
            assert task is not None
            break

    async def test_delete_nonexistent_task_returns_false(self, test_db, test_user, client):
        """Test deleting non-existent task returns False"""
        from app.database import get_session

        async for session in get_session():
            deleted = await TaskService.delete_task(session, 99999, test_user["id"])
            assert deleted is False
            break
