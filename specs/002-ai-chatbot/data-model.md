# Data Model: AI-Powered Todo Chatbot (Phase 3)

**Feature**: 002-ai-chatbot  
**Date**: 2026-04-25  
**Purpose**: Define database schema and entity relationships for chat functionality

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│  (Phase 2)      │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────┬─────────────────────┐
    │                          │                     │
    │                          │                     │
┌───▼──────────┐      ┌────────▼────────┐   ┌───────▼──────┐
│     Task     │      │  Conversation   │   │   Message    │
│  (Phase 2)   │      │     (NEW)       │   │    (NEW)     │
└──────────────┘      └────────┬────────┘   └──────────────┘
                               │                     ▲
                               │ 1:N                 │
                               └─────────────────────┘
```

---

## Entities

### 1. User (Existing - Phase 2)
**Purpose**: Represents an authenticated user of the application

**Source**: Phase 2 implementation (backend/models.py)

**Schema**:
```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(primary_key=True)  # From Better Auth
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationships**:
- One user has many tasks (1:N)
- One user has many conversations (1:N)
- One user has many messages (1:N)

**Constraints**:
- `id`: Primary key, non-null
- `email`: Unique, indexed, non-null
- `password_hash`: Non-null

**Notes**: 
- Reused from Phase 2 without modification
- User ID comes from Better Auth JWT token

---

### 2. Task (Existing - Phase 2)
**Purpose**: Represents a todo item that can be managed via web UI or chatbot

**Source**: Phase 2 implementation (backend/models.py)

**Schema**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationships**:
- Many tasks belong to one user (N:1)

**Constraints**:
- `id`: Primary key, UUID, non-null
- `user_id`: Foreign key to users.id, indexed, non-null, CASCADE delete
- `title`: 1-200 characters, non-null
- `description`: 0-2000 characters, nullable
- `completed`: Boolean, default false

**Indexes**:
- `user_id` (existing)
- `completed` (existing)
- `created_at` (existing)

**Notes**: 
- Reused from Phase 2 without modification
- Accessed by both web UI and chatbot MCP tools

---

### 3. Conversation (NEW - Phase 3)
**Purpose**: Represents a chat session between a user and the AI chatbot

**Schema**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation", cascade_delete=True)
```

**Relationships**:
- Many conversations belong to one user (N:1)
- One conversation has many messages (1:N)

**Constraints**:
- `id`: Primary key, UUID, non-null
- `user_id`: Foreign key to users.id, indexed, non-null, CASCADE delete
- `created_at`: Timestamp, non-null, default now
- `updated_at`: Timestamp, non-null, default now, auto-update on message add

**Indexes**:
- `user_id` (for listing user's conversations)
- `updated_at DESC` (for sorting by most recent activity)
- Composite: `(user_id, updated_at DESC)` (optimized query)

**Business Rules**:
- A conversation is created when user sends first message without conversation_id
- Conversations persist indefinitely (no auto-deletion)
- Users can only access their own conversations (enforced by user_id filter)
- Updated_at is updated whenever a new message is added

**State Transitions**:
- Created: When first message sent
- Active: Has messages, can receive new messages
- No explicit "closed" state (all conversations remain accessible)

---

### 4. Message (NEW - Phase 3)
**Purpose**: Represents a single message within a conversation (user or assistant)

**Schema**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(regex="^(user|assistant)$")  # Enum: user, assistant
    content: str = Field(max_length=10000)  # Message text
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Relationships**:
- Many messages belong to one conversation (N:1)
- Many messages belong to one user (N:1)

**Constraints**:
- `id`: Primary key, UUID, non-null
- `conversation_id`: Foreign key to conversations.id, indexed, non-null, CASCADE delete
- `user_id`: Foreign key to users.id, indexed, non-null, CASCADE delete
- `role`: Enum ('user', 'assistant'), non-null
- `content`: 1-10000 characters, non-null
- `created_at`: Timestamp, non-null, default now

**Indexes**:
- `conversation_id` (for loading conversation history)
- `created_at DESC` (for ordering messages chronologically)
- Composite: `(conversation_id, created_at DESC)` (optimized for last 20 messages query)

**Business Rules**:
- Role must be either 'user' or 'assistant'
- User messages created when user sends chat request
- Assistant messages created after AI generates response
- Messages are immutable (no updates, only creates)
- Messages are soft-deleted with conversation (CASCADE)
- Last 20 messages loaded per request for context

**Validation Rules**:
- `role`: Must be 'user' or 'assistant'
- `content`: 1-10000 characters (enforced by Pydantic)
- `conversation_id`: Must reference existing conversation
- `user_id`: Must match conversation.user_id (data integrity)

---

## Database Migration (Alembic)

### Migration: 002_add_conversation_message_tables.py

```python
"""Add conversation and message tables for AI chatbot

Revision ID: 002
Revises: 001
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'  # Previous migration from Phase 2
branch_labels = None
depends_on = None


def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for conversations
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'], postgresql_using='btree', postgresql_ops={'updated_at': 'DESC'})
    op.create_index('idx_conversations_user_updated', 'conversations', ['user_id', 'updated_at'], postgresql_using='btree', postgresql_ops={'updated_at': 'DESC'})
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(length=10000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for messages
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})


def downgrade():
    # Drop messages table and indexes
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('idx_messages_created_at', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')
    
    # Drop conversations table and indexes
    op.drop_index('idx_conversations_user_updated', table_name='conversations')
    op.drop_index('idx_conversations_updated_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
```

---

## Query Patterns

### 1. Load Last 20 Messages for Conversation
```python
# Optimized query using composite index
messages = await session.execute(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(20)
)
# Reverse to get chronological order (oldest first)
history = list(reversed(messages.scalars().all()))
```

**Performance**: O(log n) with index, ~1-5ms for typical conversation

---

### 2. Get User's Conversations (Most Recent First)
```python
conversations = await session.execute(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
    .limit(50)
)
```

**Performance**: O(log n) with composite index, ~1-5ms

---

### 3. Create New Conversation
```python
conversation = Conversation(
    id=str(uuid.uuid4()),
    user_id=user_id,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
session.add(conversation)
await session.commit()
```

**Performance**: O(1), ~5-10ms

---

### 4. Add Message to Conversation
```python
# Create message
message = Message(
    id=str(uuid.uuid4()),
    conversation_id=conversation_id,
    user_id=user_id,
    role=role,  # 'user' or 'assistant'
    content=content,
    created_at=datetime.utcnow()
)
session.add(message)

# Update conversation updated_at
conversation.updated_at = datetime.utcnow()

await session.commit()
```

**Performance**: O(1), ~5-10ms

---

### 5. Verify Conversation Ownership
```python
conversation = await session.execute(
    select(Conversation)
    .where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
)
if not conversation.scalar_one_or_none():
    raise HTTPException(status_code=403, detail="Access denied")
```

**Performance**: O(1) with primary key + index, ~1-2ms

---

## Data Integrity Rules

### Foreign Key Constraints
1. `conversations.user_id` → `users.id` (CASCADE DELETE)
   - When user deleted, all conversations deleted
2. `messages.conversation_id` → `conversations.id` (CASCADE DELETE)
   - When conversation deleted, all messages deleted
3. `messages.user_id` → `users.id` (CASCADE DELETE)
   - When user deleted, all messages deleted
4. `tasks.user_id` → `users.id` (CASCADE DELETE) [Existing]
   - When user deleted, all tasks deleted

### Check Constraints
1. `messages.role` IN ('user', 'assistant')
   - Ensures only valid roles stored

### Unique Constraints
- None (conversations and messages can have duplicates)

### Index Strategy
- Single-column indexes for foreign keys (user_id, conversation_id)
- Composite indexes for common query patterns (user_id + updated_at, conversation_id + created_at)
- DESC indexes for timestamp sorting

---

## Storage Estimates

### Assumptions
- Average user: 10 conversations
- Average conversation: 50 messages
- Average message: 200 characters

### Per User
- Conversations: 10 × 100 bytes = 1 KB
- Messages: 10 × 50 × 250 bytes = 125 KB
- **Total per user**: ~126 KB

### 1000 Users
- Total storage: 126 MB
- With indexes: ~200 MB

### 10,000 Users
- Total storage: 1.26 GB
- With indexes: ~2 GB

**Conclusion**: Storage requirements are minimal for expected scale.

---

## Data Retention Policy

### Current Implementation
- No automatic deletion
- All conversations and messages persist indefinitely
- Users cannot delete conversations (not in scope)

### Future Considerations
- Add soft delete flag for conversations
- Implement conversation archival after N days of inactivity
- Add user-initiated conversation deletion
- Implement GDPR-compliant data export/deletion

---

## Security Considerations

### User Isolation
- All queries MUST filter by user_id from JWT token
- Never trust user_id from request body or URL
- Verify conversation ownership before loading messages

### Data Validation
- Message content sanitized (no HTML/script injection)
- Role validated against enum
- Content length enforced (max 10,000 characters)

### Audit Trail
- created_at timestamps provide audit trail
- No message updates (immutable)
- Conversation updated_at tracks last activity

---

**Data Model Complete**: Ready for API contract definition (Phase 1 continued).
