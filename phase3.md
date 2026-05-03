# Phase III Development Guide: AI-Powered Todo Chatbot

Based on the hackathon document and your existing Phase II implementation, here's a comprehensive guide to build Phase III.

---

## Overview

**Goal**: Add a conversational AI interface to your existing TaskFlow2 web app using OpenAI Agents SDK and MCP (Model Context Protocol).

**What Users Get**: Natural language task management like:
- "Add a task to buy groceries"
- "Show me all my pending tasks"
- "Mark task 3 as complete"

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────────────────────┐     ┌─────────────┐
│  ChatKit UI │────▶│  FastAPI Backend             │────▶│  Neon DB    │
│  (Frontend) │     │  ┌────────────────────────┐  │     │  - tasks    │
│             │◀────│  │ Chat Endpoint          │  │     │  - users    │
└─────────────┘     │  │ POST /api/chat         │  │     │  - convos   │
                    │  └───────────┬────────────┘  │     │  - messages │
                    │              ▼               │     └─────────────┘
                    │  ┌────────────────────────┐  │
                    │  │ OpenAI Agents SDK      │  │
                    │  │ (Agent + Runner)       │  │
                    │  └───────────┬────────────┘  │
                    │              ▼               │
                    │  ┌────────────────────────┐  │
                    │  │ MCP Server             │  │
                    │  │ - add_task             │  │
                    │  │ - list_tasks           │  │
                    │  │ - complete_task        │  │
                    │  │ - update_task          │  │
                    │  │ - delete_task          │  │
                    │  └────────────────────────┘  │
                    └──────────────────────────────┘
```

---

## Step-by-Step Development Plan

### Phase 1: Specification (Week 1)

#### 1.1 Create Chatbot Specification

Create `specs/001-fullstack-todo-app/chatbot-spec.md`:

```markdown
# Feature: AI Chatbot for Todo Management

## User Stories

1. As a user, I can chat with an AI assistant to manage my tasks
2. As a user, I can create tasks using natural language
3. As a user, I can view my tasks by asking the chatbot
4. As a user, I can mark tasks complete through conversation
5. As a user, I can update and delete tasks via chat

## Acceptance Criteria

### Natural Language Understanding
- Bot understands "add", "create", "remember" for task creation
- Bot understands "show", "list", "what are" for viewing tasks
- Bot understands "done", "complete", "finished" for completion
- Bot understands "delete", "remove", "cancel" for deletion
- Bot understands "change", "update", "rename" for editing

### Conversation Management
- Each user has separate conversation history
- Conversations persist across sessions
- Bot maintains context within a conversation
- Server is stateless (all state in database)

### MCP Tools
- 5 tools exposed: add_task, list_tasks, complete_task, update_task, delete_task
- All tools require user_id from JWT token
- Tools return structured responses
- Tools handle errors gracefully

## Technical Requirements

### Database Models
- Conversation: id, user_id, created_at, updated_at
- Message: id, conversation_id, user_id, role (user/assistant), content, created_at

### API Endpoint
- POST /api/chat
- Request: { conversation_id?, message }
- Response: { conversation_id, response, tool_calls[] }

### Authentication
- All chat requests require JWT token
- Extract user_id from token (not from request body)
```

#### 1.2 Update Architecture Plan

Update `specs/001-fullstack-todo-app/plan.md` to include:
- MCP server architecture
- OpenAI Agents SDK integration
- Conversation state management
- ChatKit UI integration

---

### Phase 2: Database Schema (Week 1)

#### 2.1 Create Migration for New Tables

Create `backend/alembic/versions/xxx_add_chatbot_tables.py`:

```python
"""add chatbot tables

Revision ID: xxx
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),  # 'user' or 'assistant'
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Indexes
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

#### 2.2 Create SQLModel Models

Create `backend/app/models/conversation.py`:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    user_id: int = Field(foreign_key="users.id")
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

### Phase 3: Backend - MCP Server (Week 2)

#### 3.1 Install Dependencies

Update `backend/requirements.txt`:

```txt
# Existing dependencies...
openai==1.12.0
mcp==0.9.0  # Official MCP SDK
```

#### 3.2 Create MCP Tools

Create `backend/app/mcp/tools.py`:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
from sqlmodel import Session, select
from app.models.task import Task
from app.database import engine
import json

mcp_server = Server("todo-mcp-server")

@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user."""
    with Session(engine) as session:
        task = Task(
            user_id=int(user_id),
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

@mcp_server.tool()
async def list_tasks(user_id: str, status: str = "all") -> dict:
    """List tasks for the user. Status: 'all', 'pending', or 'completed'."""
    with Session(engine) as session:
        query = select(Task).where(Task.user_id == int(user_id))
        
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        
        tasks = session.exec(query).all()
        
        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ],
            "count": len(tasks)
        }

@mcp_server.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as complete."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task or task.user_id != int(user_id):
            return {"status": "error", "message": "Task not found"}
        
        task.completed = True
        session.add(task)
        session.commit()
        
        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }

@mcp_server.tool()
async def update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> dict:
    """Update task title or description."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task or task.user_id != int(user_id):
            return {"status": "error", "message": "Task not found"}
        
        if title:
            task.title = title
        if description is not None:
            task.description = description
        
        session.add(task)
        session.commit()
        
        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }

@mcp_server.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task or task.user_id != int(user_id):
            return {"status": "error", "message": "Task not found"}
        
        title = task.title
        session.delete(task)
        session.commit()
        
        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title
        }
```

---

### Phase 4: Backend - Chat Endpoint (Week 2)

#### 4.1 Create Chat Service

Create `backend/app/services/chat_service.py`:

```python
from openai import OpenAI
from sqlmodel import Session, select
from app.models.conversation import Conversation, Message
from app.mcp.tools import mcp_server
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural language.

When users want to:
- Add/create/remember something → use add_task
- See/show/list tasks → use list_tasks
- Mark something done/complete → use complete_task
- Change/update/rename a task → use update_task
- Delete/remove/cancel a task → use delete_task

Always confirm actions with friendly responses. Be concise and helpful."""

async def process_chat_message(
    user_id: int,
    message: str,
    conversation_id: int = None,
    session: Session = None
) -> dict:
    """Process a chat message and return AI response."""
    
    # Get or create conversation
    if conversation_id:
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise ValueError("Conversation not found")
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=message
    )
    session.add(user_message)
    session.commit()
    
    # Get conversation history
    history_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)
    history = session.exec(history_query).all()
    
    # Build messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend([
        {"role": msg.role, "content": msg.content}
        for msg in history
    ])
    
    # Call OpenAI with MCP tools
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=mcp_server.get_tools(),  # MCP tools
        tool_choice="auto"
    )
    
    assistant_message = response.choices[0].message
    tool_calls = []
    
    # Execute tool calls if any
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Add user_id to tool args
            tool_args["user_id"] = str(user_id)
            
            # Execute MCP tool
            result = await mcp_server.call_tool(tool_name, tool_args)
            tool_calls.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result
            })
    
    # Store assistant response
    assistant_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=assistant_message.content or ""
    )
    session.add(assistant_msg)
    session.commit()
    
    return {
        "conversation_id": conversation.id,
        "response": assistant_message.content,
        "tool_calls": tool_calls
    }
```

#### 4.2 Create Chat Route

Create `backend/app/routes/chat.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from app.database import get_session
from app.utils.auth import get_current_user
from app.services.chat_service import process_chat_message

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: int = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Send a message to the AI chatbot."""
    try:
        result = await process_chat_message(
            user_id=current_user.id,
            message=request.message,
            conversation_id=request.conversation_id,
            session=session
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Chat processing failed")
```

#### 4.3 Register Route

Update `backend/app/main.py`:

```python
from app.routes import chat

app.include_router(chat.router)
```

---

### Phase 5: Frontend - ChatKit UI (Week 3)

#### 5.1 Install Dependencies

Update `frontend/package.json`:

```json
{
  "dependencies": {
    "@openai/chatkit": "^1.0.0",
    // ... existing dependencies
  }
}
```

#### 5.2 Create Chat Page

Create `frontend/app/(dashboard)/chat/page.tsx`:

```typescript
'use client';

import { ChatKit } from '@openai/chatkit';
import { useState } from 'react';

export default function ChatPage() {
  const [conversationId, setConversationId] = useState<number | null>(null);

  const handleSendMessage = async (message: string) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_id: conversationId
      }),
      credentials: 'include' // Include JWT cookie
    });

    const data = await response.json();
    
    if (!conversationId) {
      setConversationId(data.conversation_id);
    }

    return data.response;
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AI Todo Assistant</h1>
      
      <ChatKit
        onSendMessage={handleSendMessage}
        placeholder="Ask me to manage your tasks..."
        className="h-[600px]"
      />
      
      <div className="mt-4 text-sm text-gray-600">
        <p>Try saying:</p>
        <ul className="list-disc ml-6">
          <li>"Add a task to buy groceries"</li>
          <li>"Show me all my tasks"</li>
          <li>"Mark task 3 as complete"</li>
          <li>"Delete the meeting task"</li>
        </ul>
      </div>
    </div>
  );
}
```

#### 5.3 Add Navigation Link

Update `frontend/components/layout/Navbar.tsx`:

```typescript
<nav>
  <Link href="/dashboard">Tasks</Link>
  <Link href="/chat">AI Assistant</Link>
</nav>
```

---

### Phase 6: Testing (Week 3)

#### 6.1 Backend Tests

Create `backend/tests/test_chat.py`:

```python
import pytest
from fastapi.testclient import TestClient

def test_chat_endpoint(client: TestClient, auth_headers):
    response = client.post(
        "/api/chat",
        json={"message": "Add a task to buy milk"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert len(data["tool_calls"]) > 0
    assert data["tool_calls"][0]["tool"] == "add_task"
```

#### 6.2 MCP Tools Tests

Create `backend/tests/test_mcp_tools.py`:

```python
import pytest
from app.mcp.tools import add_task, list_tasks, complete_task

@pytest.mark.asyncio
async def test_add_task():
    result = await add_task(user_id="1", title="Test Task", description="Test")
    assert result["status"] == "created"
    assert "task_id" in result

@pytest.mark.asyncio
async def test_list_tasks():
    result = await list_tasks(user_id="1", status="all")
    assert "tasks" in result
    assert "count" in result
```

---

### Phase 7: Environment Setup

#### 7.1 Backend Environment Variables

Update `backend/.env`:

```env
# Existing variables...

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# MCP Server
MCP_SERVER_PORT=3001
```

#### 7.2 Frontend Environment Variables

Update `frontend/.env.local`:

```env
# Existing variables...

# OpenAI ChatKit (if using hosted version)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
```

---

## Development Checklist

### Week 1: Planning & Database
- [ ] Create `chatbot-spec.md`
- [ ] Update `plan.md` with MCP architecture
- [ ] Create database migration
- [ ] Create Conversation and Message models
- [ ] Run migration: `alembic upgrade head`

### Week 2: Backend Implementation
- [ ] Install OpenAI and MCP dependencies
- [ ] Create 5 MCP tools (add, list, complete, update, delete)
- [ ] Create chat service with OpenAI integration
- [ ] Create `/api/chat` endpoint
- [ ] Test MCP tools individually
- [ ] Test chat endpoint with Postman

### Week 3: Frontend & Integration
- [ ] Install ChatKit dependency
- [ ] Create chat page component
- [ ] Add navigation to chat page
- [ ] Test end-to-end conversation flow
- [ ] Write backend tests
- [ ] Write frontend tests

### Week 4: Polish & Deploy
- [ ] Handle error cases gracefully
- [ ] Add loading states
- [ ] Improve AI prompts for better understanding
- [ ] Deploy to Vercel (frontend) and backend host
- [ ] Create demo video (90 seconds max)
- [ ] Submit to hackathon form

---

## Key Concepts to Understand

### 1. **Stateless Server**
- Server doesn't hold conversation state in memory
- All state stored in database (conversations, messages)
- Any server instance can handle any request
- Enables horizontal scaling

### 2. **MCP (Model Context Protocol)**
- Standard way to expose tools to AI agents
- Tools are Python functions decorated with `@mcp_server.tool()`
- OpenAI Agents SDK calls these tools automatically
- Tools return structured JSON responses

### 3. **OpenAI Agents SDK**
- Manages conversation flow
- Decides which tools to call based on user message
- Handles tool execution and response generation
- Maintains conversation context

### 4. **User Isolation**
- Always extract `user_id` from JWT token
- Never trust `user_id` from request body
- All MCP tools filter by authenticated user
- Prevents users from accessing others' tasks

---

## Common Pitfalls to Avoid

1. **Don't hardcode user_id** - Always get it from JWT token
2. **Don't skip conversation history** - AI needs context for follow-up questions
3. **Don't forget error handling** - MCP tools should handle "task not found" gracefully
4. **Don't expose internal errors** - Return user-friendly messages
5. **Don't skip testing** - Test each MCP tool independently first

---

## Resources

- **OpenAI Agents SDK**: https://platform.openai.com/docs/guides/agents
- **MCP Official SDK**: https://github.com/modelcontextprotocol/python-sdk
- **OpenAI ChatKit**: https://platform.openai.com/docs/guides/chatkit
- **Your Phase II Code**: Reference existing auth and task management

---

## Natural Language Commands Examples

The chatbot should understand and respond to:

| **User Says**                             | **Agent Should**                           |
|-------------------------------------------|--------------------------------------------|
| "Add a task to buy groceries"             | Call add_task with title "Buy groceries"   |
| "Show me all my tasks"                    | Call list_tasks with status "all"          |
| "What's pending?"                         | Call list_tasks with status "pending"      |
| "Mark task 3 as complete"                 | Call complete_task with task_id 3          |
| "Delete the meeting task"                 | Call list_tasks first, then delete_task    |
| "Change task 1 to 'Call mom tonight'"     | Call update_task with new title            |
| "I need to remember to pay bills"         | Call add_task with title "Pay bills"       |
| "What have I completed?"                  | Call list_tasks with status "completed"    |

---

## Conversation Flow (Stateless Request Cycle)

1. Receive user message
2. Fetch conversation history from database
3. Build message array for agent (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)

---

## OpenAI ChatKit Setup & Deployment

### Domain Allowlist Configuration (Required for Hosted ChatKit)

Before deploying your chatbot frontend, you must configure OpenAI's domain allowlist for security:

1. **Deploy your frontend first to get a production URL:**
   - Vercel: `https://your-app.vercel.app`
   - GitHub Pages: `https://username.github.io/repo-name`
   - Custom domain: `https://yourdomain.com`

2. **Add your domain to OpenAI's allowlist:**
   - Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter your frontend URL (without trailing slash)
   - Save changes

3. **Get your ChatKit domain key:**
   - After adding the domain, OpenAI will provide a domain key
   - Pass this key to your ChatKit configuration

**Note**: The hosted ChatKit option only works after adding the correct domains under Security → Domain Allowlist. Local development (`localhost`) typically works without this configuration.

---

## Key Architecture Benefits

| **Aspect**           | **Benefit**                                             |
|----------------------|---------------------------------------------------------|
| **MCP Tools**        | Standardized interface for AI to interact with your app |
| **Single Endpoint**  | Simpler API — AI handles routing to tools               |
| **Stateless Server** | Scalable, resilient, horizontally scalable              |
| **Tool Composition** | Agent can chain multiple tools in one turn              |

### Key Stateless Architecture Benefits

- **Scalability:** Any server instance can handle any request
- **Resilience:** Server restarts don't lose conversation state
- **Horizontal scaling:** Load balancer can route to any backend
- **Testability:** Each request is independent and reproducible

---

## Next Steps

1. **Start with Spec**: Create `chatbot-spec.md` following SDD principles
2. **Database First**: Add conversation tables before writing code
3. **Test MCP Tools**: Make sure each tool works independently
4. **Integrate Gradually**: Chat endpoint → Frontend → Polish

---

## Submission Requirements for Phase III

### Required Deliverables

1. **GitHub Repository** containing:
   - All Phase III source code
   - `/specs/001-fullstack-todo-app/chatbot-spec.md`
   - Updated `plan.md` and `tasks.md`
   - Database migration scripts
   - README with Phase III setup instructions

2. **Deployed Application**:
   - Frontend URL (Vercel)
   - Backend API URL
   - Working chatbot interface

3. **Demo Video** (maximum 90 seconds):
   - Show natural language task creation
   - Demonstrate conversation context
   - Show MCP tools in action
   - Display task list updates

4. **WhatsApp Number** for presentation invitation

---

## Success Criteria

Phase III is complete when:

- [ ] Users can create tasks via natural language
- [ ] Users can list tasks by asking the chatbot
- [ ] Users can mark tasks complete through conversation
- [ ] Users can update and delete tasks via chat
- [ ] Conversation history persists across sessions
- [ ] Server is stateless (all state in database)
- [ ] All 5 MCP tools work correctly
- [ ] User isolation is enforced (JWT-based)
- [ ] Error handling is graceful
- [ ] Tests pass for chat endpoint and MCP tools

---

**Good luck with Phase III! 🚀**

*Remember: Follow Spec-Driven Development - Write spec → Generate plan → Break into tasks → Implement via Claude Code*
