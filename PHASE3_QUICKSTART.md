# Phase III Quick Start Guide

**Last Updated**: 2026-04-24

This is a condensed guide to get you started with Phase III development immediately. For full details, see `phase3.md`.

---

## What You're Building

Add an AI chatbot to your existing TaskFlow2 app that lets users manage tasks through natural language:

```
User: "Add a task to buy groceries"
Bot: "✓ Created task: Buy groceries (Task #5)"

User: "Show me my pending tasks"
Bot: "You have 3 pending tasks:
     1. Buy groceries
     2. Call mom
     3. Finish report"
```

---

## Prerequisites

- ✅ Phase II completed (TaskFlow2 web app working)
- ✅ OpenAI API key (get from https://platform.openai.com/api-keys)
- ✅ Existing authentication and task management working

---

## Quick Setup (30 Minutes)

### Step 1: Add Environment Variables

**Backend** (`backend/.env`):
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key  # Optional for hosted ChatKit
```

### Step 2: Install Dependencies

**Backend**:
```bash
cd backend
pip install openai==1.12.0 mcp==0.9.0
```

**Frontend**:
```bash
cd frontend
npm install @openai/chatkit
```

### Step 3: Create Database Tables

Run this SQL or create an Alembic migration:

```sql
-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

---

## File Structure to Create

```
backend/
├── app/
│   ├── models/
│   │   └── conversation.py          # NEW: Conversation & Message models
│   ├── mcp/
│   │   └── tools.py                 # NEW: 5 MCP tools
│   ├── services/
│   │   └── chat_service.py          # NEW: OpenAI integration
│   └── routes/
│       └── chat.py                  # NEW: POST /api/chat endpoint

frontend/
└── app/
    └── (dashboard)/
        └── chat/
            └── page.tsx             # NEW: ChatKit UI
```

---

## Implementation Order

### Day 1: Database & Models
1. Create database migration
2. Create `backend/app/models/conversation.py`
3. Run migration: `alembic upgrade head`

### Day 2: MCP Tools
1. Create `backend/app/mcp/tools.py`
2. Implement 5 tools: add_task, list_tasks, complete_task, update_task, delete_task
3. Test each tool individually

### Day 3: Chat Endpoint
1. Create `backend/app/services/chat_service.py`
2. Create `backend/app/routes/chat.py`
3. Register route in `main.py`
4. Test with Postman/curl

### Day 4: Frontend
1. Create `frontend/app/(dashboard)/chat/page.tsx`
2. Add navigation link
3. Test end-to-end

---

## Minimal Working Example

### Backend: MCP Tool (Simplified)

```python
# backend/app/mcp/tools.py
from mcp.server import Server

mcp_server = Server("todo-mcp")

@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task."""
    # Your existing task creation logic here
    task = create_task_in_db(int(user_id), title, description)
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }
```

### Backend: Chat Endpoint (Simplified)

```python
# backend/app/routes/chat.py
from fastapi import APIRouter, Depends
from openai import OpenAI
from app.mcp.tools import mcp_server

router = APIRouter()
client = OpenAI()

@router.post("/api/chat")
async def chat(message: str, current_user = Depends(get_current_user)):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a todo assistant."},
            {"role": "user", "content": message}
        ],
        tools=mcp_server.get_tools()
    )
    
    # Execute tool calls and return response
    return {"response": response.choices[0].message.content}
```

### Frontend: Chat Page (Simplified)

```typescript
// frontend/app/(dashboard)/chat/page.tsx
'use client';

import { ChatKit } from '@openai/chatkit';

export default function ChatPage() {
  const handleSendMessage = async (message: string) => {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
      credentials: 'include'
    });
    
    const data = await res.json();
    return data.response;
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AI Todo Assistant</h1>
      <ChatKit onSendMessage={handleSendMessage} />
    </div>
  );
}
```

---

## Testing Your Implementation

### Test MCP Tools Directly

```python
# Test in Python console
from app.mcp.tools import add_task, list_tasks
import asyncio

# Add a task
result = asyncio.run(add_task(user_id="1", title="Test Task"))
print(result)  # Should show: {"task_id": X, "status": "created", ...}

# List tasks
result = asyncio.run(list_tasks(user_id="1", status="all"))
print(result)  # Should show: {"tasks": [...], "count": N}
```

### Test Chat Endpoint with curl

```bash
# Get JWT token first (from your existing login)
TOKEN="your-jwt-token"

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy milk"}'
```

### Test Frontend

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to: `http://localhost:3000/chat`
4. Type: "Add a task to buy groceries"
5. Verify task appears in database and regular task list

---

## Common Issues & Solutions

### Issue: "OpenAI API key not found"
**Solution**: Make sure `OPENAI_API_KEY` is in `backend/.env` and restart server

### Issue: "MCP tools not being called"
**Solution**: Check that tools are properly decorated with `@mcp_server.tool()` and registered

### Issue: "Conversation not persisting"
**Solution**: Verify conversation_id is being stored and passed back to frontend

### Issue: "User can see other users' tasks"
**Solution**: Always extract user_id from JWT token, never from request body

### Issue: "ChatKit not loading"
**Solution**: Check that `@openai/chatkit` is installed and domain is allowlisted (for production)

---

## Development Workflow (SDD)

Following Spec-Driven Development:

1. **Specify**: Create `specs/001-fullstack-todo-app/chatbot-spec.md`
2. **Plan**: Update `specs/001-fullstack-todo-app/plan.md` with architecture
3. **Tasks**: Update `specs/001-fullstack-todo-app/tasks.md` with implementation tasks
4. **Implement**: Use Claude Code to generate code from tasks

---

## Key Reminders

✅ **DO**:
- Extract user_id from JWT token
- Store all conversation state in database
- Test each MCP tool independently
- Handle errors gracefully
- Keep server stateless

❌ **DON'T**:
- Trust user_id from request body
- Store conversation state in memory
- Skip error handling
- Expose internal errors to users
- Hardcode API keys

---

## Next Steps After Basic Implementation

Once you have the basic chatbot working:

1. **Improve AI Understanding**: Enhance system prompt for better natural language processing
2. **Add Context**: Make bot remember previous tasks mentioned in conversation
3. **Error Messages**: Improve user-facing error messages
4. **Loading States**: Add loading indicators in UI
5. **Conversation History**: Show past conversations in sidebar
6. **Voice Input**: Add speech-to-text for voice commands (bonus points!)

---

## Resources

- **Full Guide**: See `phase3.md` for complete implementation details
- **Hackathon Doc**: See `_MConverter.eu_Hackathon II - Todo Spec-Driven Development.md`
- **OpenAI Docs**: https://platform.openai.com/docs
- **MCP SDK**: https://github.com/modelcontextprotocol/python-sdk

---

## Submission Checklist

Before submitting Phase III:

- [ ] Chatbot can create tasks via natural language
- [ ] Chatbot can list tasks (all/pending/completed)
- [ ] Chatbot can mark tasks complete
- [ ] Chatbot can update task details
- [ ] Chatbot can delete tasks
- [ ] Conversation history persists
- [ ] User isolation enforced (JWT-based)
- [ ] Tests written and passing
- [ ] Demo video created (max 90 seconds)
- [ ] Deployed to Vercel + backend host
- [ ] Submitted via hackathon form

---

**Estimated Time**: 3-4 days for basic implementation, 1 week for polished version

**Due Date**: December 21, 2025 (from hackathon schedule)

**Points**: 200 points (+ bonus points for advanced features)

---

Good luck! 🚀

*For detailed implementation code, architecture diagrams, and advanced features, refer to `phase3.md`*
