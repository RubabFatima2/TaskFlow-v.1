# Data Model: Full-Stack Todo Web Application

**Feature**: 001-fullstack-todo-app  
**Date**: 2026-04-10  
**Status**: Complete

## Overview

This document defines the data models, entities, relationships, and validation rules for the todo application. The data model supports multi-user task management with authentication and user-level data isolation.

## Entity Relationship Diagram

```
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ id (PK)            │
│ email (UNIQUE)     │
│ password_hash      │
│ created_at         │
│ updated_at         │
└─────────────────────┘
          │
          │ 1:N
          │
          ▼
┌─────────────────────┐
│       tasks         │
├─────────────────────┤
│ id (PK)            │
│ user_id (FK)       │◄─── References users.id
│ title              │
│ description        │
│ completed          │
│ created_at         │
│ updated_at         │
└─────────────────────┘
```

## Entities

### 1. User Entity

**Purpose**: Represents an authenticated user account

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| email | String(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| password_hash | String(255) | NOT NULL | Bcrypt/Argon2 hashed password |
| created_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email must be unique across all users
- Password must be minimum 8 characters before hashing
- Password hash must use bcrypt (cost factor 12) or Argon2id
- Email is case-insensitive (normalize to lowercase before storage)

**Indexes**:
- Primary key index on `id` (automatic)
- Unique index on `email` for fast login lookups

**State Transitions**: None (users are created and remain active; soft delete can be added later)

**SQLModel Definition** (Backend):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**TypeScript Type** (Frontend):
```typescript
export interface User {
  id: number;
  email: string;
  created_at: string; // ISO 8601 format
  updated_at: string; // ISO 8601 format
}

// Note: password_hash is never sent to frontend
```

---

### 2. Task Entity

**Purpose**: Represents a todo item owned by a user

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| user_id | Integer | FOREIGN KEY (users.id), NOT NULL, ON DELETE CASCADE | Owner of the task |
| title | String(200) | NOT NULL | Task title/summary |
| description | Text | NULLABLE | Optional detailed description |
| completed | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| updated_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Validation Rules**:
- Title must be 1-200 characters (non-empty, trimmed)
- Description is optional, max 10,000 characters
- Completed must be boolean (true/false)
- user_id must reference an existing user
- Title cannot be only whitespace

**Indexes**:
- Primary key index on `id` (automatic)
- Index on `user_id` for filtering tasks by user (critical for performance)
- Index on `completed` for filtering by completion status
- Index on `created_at` for sorting by creation date

**Foreign Key Constraints**:
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE
  - When a user is deleted, all their tasks are automatically deleted

**State Transitions**:
```
[Created] ──────────────────────────────────────────┐
  │                                                  │
  │ completed = false (default)                      │
  │                                                  │
  ▼                                                  │
[Incomplete] ◄──────────────────────────────────────┤
  │                                                  │
  │ Mark as complete (completed = true)              │
  │                                                  │
  ▼                                                  │
[Complete] ─────────────────────────────────────────┘
  │ Mark as incomplete (completed = false)
  │
  └──────────────────────────────────────────────────►
```

**SQLModel Definition** (Backend):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**TypeScript Type** (Frontend):
```typescript
export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string; // ISO 8601 format
  updated_at: string; // ISO 8601 format
}
```

---

## Pydantic Schemas (Request/Response)

### Authentication Schemas

```python
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    """Request schema for user registration"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

class UserLogin(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Response schema for user data (no password)"""
    id: int
    email: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Response schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires
```

### Task Schemas

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    """Request schema for creating a task"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10000)

class TaskUpdate(BaseModel):
    """Request schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10000)
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    """Response schema for task data"""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Response schema for list of tasks"""
    tasks: list[TaskResponse]
    total: int
```

---

## Database Migrations

### Initial Migration (Alembic)

**Migration**: `001_create_users_and_tasks_tables.py`

```python
"""Create users and tasks tables

Revision ID: 001
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])
    
    # Create trigger for updated_at auto-update (PostgreSQL)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;')
```

---

## Data Access Patterns

### User Queries

```python
# Create user
async def create_user(session: AsyncSession, email: str, password_hash: str) -> User:
    user = User(email=email.lower(), password_hash=password_hash)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Get user by email
async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email.lower())
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# Get user by id
async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()
```

### Task Queries (with User Isolation)

```python
# Create task (user_id from JWT)
async def create_task(session: AsyncSession, user_id: int, title: str, description: Optional[str]) -> Task:
    task = Task(user_id=user_id, title=title.strip(), description=description)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

# Get all tasks for user
async def get_user_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    result = await session.execute(statement)
    return result.scalars().all()

# Get single task (with ownership check)
async def get_task_by_id(session: AsyncSession, task_id: int, user_id: int) -> Optional[Task]:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# Update task (with ownership check)
async def update_task(session: AsyncSession, task_id: int, user_id: int, updates: dict) -> Optional[Task]:
    task = await get_task_by_id(session, task_id, user_id)
    if not task:
        return None
    
    for key, value in updates.items():
        if value is not None:
            setattr(task, key, value)
    
    await session.commit()
    await session.refresh(task)
    return task

# Delete task (with ownership check)
async def delete_task(session: AsyncSession, task_id: int, user_id: int) -> bool:
    task = await get_task_by_id(session, task_id, user_id)
    if not task:
        return False
    
    await session.delete(task)
    await session.commit()
    return True
```

---

## Security Considerations

### User Data Isolation
- **CRITICAL**: All task queries MUST include `WHERE user_id = {authenticated_user_id}`
- Never trust `user_id` from request body or URL parameters
- Always extract `user_id` from verified JWT token
- Return 403 Forbidden if user attempts to access another user's task

### Password Security
- Never store plaintext passwords
- Use bcrypt (cost factor 12) or Argon2id for hashing
- Never return `password_hash` in API responses
- Validate password strength on registration (minimum 8 characters)

### Data Validation
- Validate all inputs with Pydantic schemas
- Trim whitespace from title before storage
- Reject empty titles (after trimming)
- Enforce maximum lengths to prevent DoS attacks

---

## Summary

The data model consists of two entities:
1. **User**: Authentication and ownership
2. **Task**: Todo items with user isolation

Key design decisions:
- Foreign key with CASCADE delete for automatic cleanup
- Indexes on user_id, completed, created_at for query performance
- Triggers for automatic updated_at timestamp updates
- Pydantic schemas for request/response validation
- User data isolation enforced at query level

All validation rules and constraints are documented and ready for implementation.
