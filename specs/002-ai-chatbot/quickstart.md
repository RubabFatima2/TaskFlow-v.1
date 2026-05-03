# Quickstart Guide: AI-Powered Todo Chatbot (Phase 3)

**Feature**: 002-ai-chatbot  
**Date**: 2026-04-25  
**Purpose**: Setup instructions for developers implementing the AI chatbot feature

---

## Prerequisites

### Phase 2 Requirements (Must be complete)
- ✅ Backend FastAPI application running
- ✅ Frontend Next.js application running
- ✅ Neon PostgreSQL database configured
- ✅ Better Auth JWT authentication working
- ✅ Task CRUD operations functional
- ✅ User registration and login working

### New Requirements (Phase 3)
- Python 3.11+ installed
- Node.js 18+ installed
- Gemini API key (from Google AI Studio)
- Git repository on branch `002-ai-chatbot`

---

## Environment Setup

### 1. Obtain Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the API key (starts with `AIza...`)
5. Store securely (will be added to `.env` file)

### 2. Backend Environment Variables

Add to `backend/.env`:

```bash
# Existing Phase 2 variables (keep these)
DATABASE_URL=postgresql://user:password@host:5432/taskflow2
BETTER_AUTH_SECRET=your_shared_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# NEW Phase 3 variables
GEMINI_API_KEY=AIza...your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 3. Frontend Environment Variables

Add to `frontend/.env.local`:

```bash
# Existing Phase 2 variables (keep these)
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your_shared_secret_here

# No new Phase 3 variables needed for frontend
```

**IMPORTANT**: `BETTER_AUTH_SECRET` must be identical in both frontend and backend.

---

## Installation

### Backend Dependencies

1. Navigate to backend directory:
```bash
cd backend
```

2. Install new Python packages:
```bash
pip install google-generativeai==0.3.2
pip install python-jose[cryptography]==3.3.0  # If not already installed
```

3. Update `requirements.txt`:
```bash
pip freeze > requirements.txt
```

### Frontend Dependencies

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install new npm packages:
```bash
npm install @chatscope/chat-ui-kit-react@^2.0.0
npm install @chatscope/chat-ui-kit-styles@^1.4.0
```

---

## Database Migration

### 1. Create Migration File

```bash
cd backend
alembic revision -m "add_conversation_message_tables"
```

This creates a new migration file in `backend/alembic/versions/`.

### 2. Edit Migration File

Copy the migration code from `specs/002-ai-chatbot/data-model.md` (section: Database Migration) into the generated file.

### 3. Run Migration

```bash
alembic upgrade head
```

### 4. Verify Tables Created

```bash
# Connect to database and verify
psql $DATABASE_URL -c "\dt"
```

Expected output should include:
- `conversations`
- `messages`
- `tasks` (existing)
- `users` (existing)

### 5. Verify Indexes

```bash
psql $DATABASE_URL -c "\di"
```

Expected indexes:
- `idx_conversations_user_id`
- `idx_conversations_updated_at`
- `idx_conversations_user_updated`
- `idx_messages_conversation_id`
- `idx_messages_created_at`
- `idx_messages_conversation_created`

---

## Project Structure

### Backend Files to Create

```
backend/
├── app/
│   ├── models/
│   │   ├── conversation.py          # NEW
│   │   └── message.py               # NEW
│   ├── routes/
│   │   └── chat.py                  # NEW
│   ├── services/
│   │   ├── agent_service.py         # NEW
│   │   └── gemini_service.py        # NEW
│   └── mcp/
│       ├── __init__.py              # NEW
│       ├── tools.py                 # NEW
│       └── schemas.py               # NEW
└── tests/
    ├── test_chat_endpoint.py        # NEW
    ├── test_mcp_tools.py            # NEW
    └── test_agent_service.py        # NEW
```

### Frontend Files to Create

```
frontend/
├── app/
│   └── chat/
│       └── page.tsx                 # NEW
└── components/
    └── chat/
        ├── ChatInterface.tsx        # NEW
        ├── MessageList.tsx          # NEW
        └── MessageInput.tsx         # NEW
```

---

## Development Workflow

### 1. Start Backend (Terminal 1)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Expected output:
```
  ▲ Next.js 16.0.0
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

### 3. Verify Phase 2 Still Works

1. Open browser: http://localhost:3000
2. Register/login with test user
3. Create a task via web UI
4. Verify task appears in list
5. Complete/delete task via web UI

**If Phase 2 broken**: Stop and fix before continuing with Phase 3.

### 4. Test Gemini API Connection

Create test script `backend/test_gemini.py`:

```python
import os
from google import generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")

response = model.generate_content("Say hello")
print(response.text)
```

Run:
```bash
cd backend
python test_gemini.py
```

Expected output: "Hello!" or similar greeting.

**If error**: Check `GEMINI_API_KEY` in `.env` file.

---

## Testing Strategy

### Unit Tests (Backend)

```bash
cd backend
pytest tests/test_mcp_tools.py -v
pytest tests/test_agent_service.py -v
```

### Integration Tests (Backend)

```bash
pytest tests/test_chat_endpoint.py -v
```

### E2E Tests (Frontend + Backend)

```bash
cd frontend
npm run test:e2e
```

### Manual Testing Checklist

- [ ] Send chat message "add buy groceries"
- [ ] Verify task created in database
- [ ] Send "show my tasks"
- [ ] Verify tasks listed in response
- [ ] Send "mark buy groceries as done"
- [ ] Verify task completed in database
- [ ] Send "delete buy groceries"
- [ ] Verify task deleted from database
- [ ] Test conversation persistence (reload page, history preserved)
- [ ] Test with invalid JWT token (should return 401)
- [ ] Test with another user's conversation_id (should return 403)

---

## Architecture Overview

### Request Flow

```
1. User types message in chat UI (frontend)
   ↓
2. Frontend sends POST /api/v1/chat with JWT token
   ↓
3. JWT middleware extracts user_id from token
   ↓
4. Chat endpoint loads last 20 messages from DB
   ↓
5. Agent service calls Gemini API with message + history + tools
   ↓
6. Gemini returns function calls (e.g., add_task)
   ↓
7. Agent service executes MCP tools
   ↓
8. Agent service calls Gemini again with tool results
   ↓
9. Gemini generates natural language response
   ↓
10. Chat endpoint saves messages to DB
   ↓
11. Response sent to frontend
   ↓
12. Chat UI displays assistant message
```

### Key Components

**Backend**:
- `chat.py`: FastAPI endpoint for POST /api/v1/chat
- `agent_service.py`: Orchestrates Gemini API calls and tool execution
- `gemini_service.py`: Wrapper for Gemini API client
- `mcp/tools.py`: MCP tool implementations (add_task, list_tasks, etc.)
- `models/conversation.py`: Conversation SQLModel
- `models/message.py`: Message SQLModel

**Frontend**:
- `app/chat/page.tsx`: Chat page route
- `components/chat/ChatInterface.tsx`: Main chat component
- `components/chat/MessageList.tsx`: Message history display
- `components/chat/MessageInput.tsx`: Input field with send button

---

## Common Issues & Solutions

### Issue: "Invalid API key" error from Gemini

**Solution**: 
1. Verify `GEMINI_API_KEY` in `backend/.env`
2. Check API key is active in Google AI Studio
3. Restart backend server after updating `.env`

### Issue: "Table 'conversations' does not exist"

**Solution**:
```bash
cd backend
alembic upgrade head
```

### Issue: JWT token verification fails

**Solution**:
1. Verify `BETTER_AUTH_SECRET` matches in frontend and backend
2. Check JWT token format in Authorization header: `Bearer <token>`
3. Verify token not expired (15 minute default)

### Issue: Chat UI not rendering

**Solution**:
1. Verify `@chatscope/chat-ui-kit-styles` imported in layout
2. Check browser console for errors
3. Verify API endpoint URL in frontend config

### Issue: "User ID mismatch" error

**Solution**:
1. Verify JWT middleware extracting user_id correctly
2. Check agent service injecting user_id into tool calls
3. Verify conversation.user_id matches JWT user_id

### Issue: Gemini not calling tools

**Solution**:
1. Check tool descriptions are clear and specific
2. Verify tool schemas match Gemini function calling format
3. Test with explicit commands: "use add_task tool to create task"
4. Check Gemini API logs for function call responses

---

## Performance Optimization

### Database Query Optimization
- Indexes already created by migration
- Monitor query performance with `EXPLAIN ANALYZE`
- Consider connection pooling for high load

### Gemini API Optimization
- Use `gemini-2.0-flash-exp` (fastest model)
- Implement request timeout (30 seconds)
- Cache tool schemas (don't regenerate per request)
- Consider streaming responses for long conversations

### Frontend Optimization
- Lazy load chat history (load on scroll)
- Debounce input field (prevent rapid requests)
- Show loading states during AI processing
- Cache conversation list

---

## Security Checklist

- [ ] `GEMINI_API_KEY` in `.env` file (not committed to git)
- [ ] `BETTER_AUTH_SECRET` in `.env` files (not committed to git)
- [ ] `.env` and `.env.local` in `.gitignore`
- [ ] JWT token verified on every chat request
- [ ] User ID extracted from JWT, never from request body
- [ ] Conversation ownership verified before loading messages
- [ ] Task ownership verified in all MCP tools
- [ ] Input validation with Pydantic models
- [ ] Error messages don't expose sensitive data
- [ ] HTTPS enabled in production

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (unit, integration, e2e)
- [ ] Database migration tested in staging
- [ ] Environment variables configured in production
- [ ] Gemini API key valid and has sufficient quota
- [ ] Rate limiting configured for chat endpoint
- [ ] Error tracking enabled (Sentry, etc.)
- [ ] Logging configured for production

### Deployment Steps
1. Run database migration in production
2. Deploy backend with new environment variables
3. Deploy frontend with updated dependencies
4. Verify health check endpoint
5. Test chat functionality with production data
6. Monitor error logs for first 24 hours

### Post-Deployment
- [ ] Monitor Gemini API usage and costs
- [ ] Monitor database performance (query times)
- [ ] Monitor error rates for chat endpoint
- [ ] Collect user feedback on chatbot accuracy
- [ ] Review conversation logs for improvement opportunities

---

## Next Steps

After completing this quickstart:

1. **Review Spec**: Read `specs/002-ai-chatbot/spec.md` for full requirements
2. **Review Plan**: Read `specs/002-ai-chatbot/plan.md` for architecture decisions
3. **Review Contracts**: Read `specs/002-ai-chatbot/contracts/` for API details
4. **Generate Tasks**: Run `/sp.tasks` to generate implementation tasks
5. **Implement**: Follow TDD workflow (Red-Green-Refactor)

---

## Support & Resources

### Documentation
- [Gemini API Docs](https://ai.google.dev/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Better Auth Docs](https://www.better-auth.com/docs)
- [Chatscope UI Kit](https://chatscope.io/storybook/react/)

### Troubleshooting
- Check `backend/logs/` for error logs
- Check browser console for frontend errors
- Use `pytest -v` for detailed test output
- Use `alembic history` to verify migrations

### Getting Help
- Review spec files in `specs/002-ai-chatbot/`
- Check CLAUDE.md for project-specific instructions
- Review constitution.md for coding standards

---

**Quickstart Complete**: Development environment ready for Phase 2 (tasks.md generation).
