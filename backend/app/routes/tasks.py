from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.task_service import TaskService
from app.utils.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.middleware.rate_limit import tasks_rate_limit

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(tasks_rate_limit)
):
    """Create a new task for the authenticated user"""
    task = await TaskService.create_task(session, current_user.id, task_data)
    return task


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    completed: bool = Query(None, description="Filter by completion status"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(tasks_rate_limit)
):
    """Get all tasks for the authenticated user with pagination"""
    tasks, total = await TaskService.get_user_tasks(
        session, current_user.id, skip=skip, limit=limit, completed=completed
    )
    return {"tasks": tasks, "total": total}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(tasks_rate_limit)
):
    """Get a single task by ID"""
    task = await TaskService.get_task_by_id(session, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(tasks_rate_limit)
):
    """Update a task"""
    task = await TaskService.update_task(session, task_id, current_user.id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(tasks_rate_limit)
):
    """Delete a task"""
    deleted = await TaskService.delete_task(session, task_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return None
