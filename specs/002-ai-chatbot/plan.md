# Implementation Plan: AI-Powered Todo Chatbot (Phase 3)

**Branch**: `002-ai-chatbot` | **Date**: 2026-04-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add AI-powered natural language interface to existing TaskFlow2 todo application, enabling users to create, view, update, complete, and delete tasks through conversational chat. Uses Gemini API (gemini-2.0-flash) for natural language understanding, OpenAI Agents SDK for agent orchestration, and Official MCP Python SDK for tool definitions. Reuses existing Phase 2 JWT authentication, Task model, and database connection. Adds new Conversation and Message tables for persistent chat history.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript (frontend Next.js 16+)
**Primary Dependencies**: 
- Backend: FastAPI, SQLModel, google-generativeai (Gemini API), openai-agents-sdk, mcp-python-sdk, python-jose (JWT), alembic
- Frontend: Next.js 16+ (App Router), Better Auth, @openai/chatkit or equivalent React chat UI library, Tailwind CSS
**Storage**: Neon Serverless PostgreSQL (existing from Phase 2, adding Conversation + Message tables)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web (monorepo with frontend/ and backend/ directories)
**Performance Goals**: 
- Chat endpoint response < 3 seconds (excluding AI processing time)
- API endpoints < 200ms for simple queries
- Support 100 concurrent users without degradation
**Constraints**: 
- MUST reuse Phase 2 JWT middleware, Task model, and DB connection without modification
- MUST NOT use OpenAI GPT models (Gemini only)
- MUST extract user_id from JWT token only (never from request body/URL)
- Stateless backend (all state in Neon DB)
- Load last 20 messages as conversation context per request
**Scale/Scope**: 
- 5 MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
- 1 new chat endpoint (POST /api/v1/chat)
- 2 new database tables (Conversation, Message)
- 7 user stories (P1: 2, P2: 3, P3: 2)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Technology Stack Compliance ✅
- **Frontend**: Next.js 16+ (App Router) ✅, TypeScript ✅, Tailwind CSS ✅
- **Backend**: Python FastAPI ✅, SQLModel ✅, Pydantic ✅
- **Database**: Neon Serverless PostgreSQL ✅, Alembic migrations ✅
- **Authentication**: Better Auth (frontend) ✅ + JWT verification (backend) ✅
- **Monorepo Structure**: frontend/ and backend/ directories ✅

### Authentication & Authorization (Principle VII) ✅
- User ID extracted from JWT token only (never from request body/URL) ✅
- Shared secret (BETTER_AUTH_SECRET) between frontend and backend ✅
- All chat endpoints require authentication ✅
- User-level data isolation enforced (users only access their own conversations/tasks) ✅
- JWT verification middleware reused from Phase 2 ✅

### API-First Architecture (Principle IV) ✅
- RESTful endpoint: POST /api/v1/chat ✅
- User ID from JWT, not URL path ✅
- Standard HTTP status codes (200, 400, 401, 403, 404, 500, 503) ✅
- JSON request/response with clear schemas ✅
- Stateless API design ✅

### Test-First Development (Principle II) ⚠️
- **GATE REQUIREMENT**: TDD mandatory for all implementation
- Tests must be written and approved before implementation begins
- Minimum 70% code coverage for business logic
- 100% coverage for critical paths (chat endpoint, MCP tools, JWT verification)
- **ACTION REQUIRED**: Phase 2 (tasks.md) must include test cases for each task

### Security by Default (Principle III) ✅
- All inputs validated via Pydantic ✅
- Secrets in environment variables (GEMINI_API_KEY, BETTER_AUTH_SECRET, DATABASE_URL) ✅
- No sensitive data in logs ✅
- User isolation enforced at database query level ✅
- JWT token validation on every request ✅

### Data Integrity (Principle VI) ✅
- Foreign key constraints (conversations.user_id → users.id, messages.conversation_id → conversations.id) ✅
- Clear error messages for operation failures ✅
- Database indexes on frequently queried fields ✅

### Spec-Driven Development Workflow (Principle XIV) ✅
- Specification phase complete (spec.md) ✅
- Planning phase in progress (plan.md) ✅
- Task generation phase next (tasks.md) ⏳
- Implementation via Claude Code only ⏳

### Performance Standards ✅
- Chat endpoint < 3 seconds (excluding AI processing) ✅
- API endpoints < 200ms for simple queries ✅
- Database queries < 100ms with indexes ✅
- Support 100 concurrent users ✅

### Accessibility Standards (Principle XI) ⏳
- **ACTION REQUIRED**: Frontend chat UI must meet WCAG 2.1 Level AA
- Keyboard navigation for chat interface
- ARIA labels for chat messages and input
- Screen reader support for conversation history

### Error Handling & User Experience (Principle XII) ✅
- User-friendly error messages (no stack traces) ✅
- Graceful handling of Gemini API failures (503 Service Unavailable) ✅
- Clear recovery paths for users ✅
- Error logging with context ✅

### Rate Limiting & Abuse Prevention (Principle XIII) ⏳
- **ACTION REQUIRED**: Implement rate limiting for chat endpoint
- Recommended: 30 requests per minute per user (write endpoint)
- Return 429 Too Many Requests with Retry-After header
- Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)

**GATE STATUS**: ✅ PASS (with action items for Phase 2 tasks.md)
- All mandatory principles satisfied
- Action items identified for implementation phase
- No blocking violations

---

## Constitution Check Re-evaluation (Post Phase 1 Design)

*Re-check after Phase 1 design artifacts complete*

### Technology Stack Compliance ✅
- All technologies confirmed and documented in research.md
- Dependencies identified: google-generativeai, @chatscope/chat-ui-kit-react
- No deviations from mandated stack

### Architecture Decisions ✅
- **ADR-001**: Use Gemini API directly instead of OpenAI Agents SDK
  - Rationale: OpenAI Agents SDK not compatible with Gemini
  - Impact: Custom agent loop implementation required
  - Status: Documented in research.md
- **ADR-002**: Use @chatscope/chat-ui-kit-react instead of OpenAI Chatkit
  - Rationale: OpenAI Chatkit not publicly available
  - Impact: Custom API integration needed
  - Status: Documented in research.md
- **ADR-003**: Custom MCP tool implementation (conditional)
  - Rationale: Official MCP SDK may not be mature
  - Impact: Fallback to custom implementation if needed
  - Status: Documented in research.md

### Data Model Validation ✅
- Conversation and Message entities defined with proper relationships
- Foreign key constraints enforce data integrity
- Indexes optimize query performance
- Migration strategy documented and safe (non-breaking)

### API Contracts Validation ✅
- OpenAPI 3.0 spec created for chat endpoint
- MCP tool schemas defined with Gemini function calling format
- Request/response schemas documented
- Error responses standardized

### Security Re-check ✅
- User ID injection strategy confirmed (JWT → agent service → tools)
- Conversation ownership verification documented
- Input validation with Pydantic models
- Error messages don't expose internals

### Performance Re-check ✅
- Database indexes designed for optimal query performance
- Last 20 messages strategy validated (2000-4000 tokens, well within Gemini limit)
- Gemini API timeout strategy defined (30 seconds)
- No performance bottlenecks identified

### Accessibility Re-check ⏳
- Frontend chat UI library selected (@chatscope/chat-ui-kit-react)
- WCAG 2.1 AA compliance required in tasks.md
- Keyboard navigation and ARIA labels to be implemented

### Rate Limiting Re-check ⏳
- Strategy defined (30 req/min per user for chat endpoint)
- Implementation details to be specified in tasks.md

**FINAL GATE STATUS**: ✅ PASS
- All design decisions documented
- No constitution violations
- Ready for Phase 2 (tasks.md generation)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                      # FastAPI app entry point (existing)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py                  # Task model (existing, reused)
│   │   ├── conversation.py          # NEW: Conversation model
│   │   └── message.py               # NEW: Message model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py                 # Task CRUD routes (existing, reused)
│   │   └── chat.py                  # NEW: Chat endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_service.py         # NEW: OpenAI Agents SDK integration
│   │   └── gemini_service.py        # NEW: Gemini API client
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── tools.py                 # NEW: MCP tool definitions
│   │   └── schemas.py               # NEW: MCP tool schemas
│   ├── middleware/
│   │   └── auth.py                  # JWT middleware (existing, reused)
│   └── db.py                        # Database connection (existing, reused)
├── alembic/
│   ├── versions/
│   │   └── 002_add_conversation_message_tables.py  # NEW: Migration
│   └── env.py
├── tests/
│   ├── test_chat_endpoint.py       # NEW: Chat endpoint tests
│   ├── test_mcp_tools.py            # NEW: MCP tool tests
│   └── test_agent_service.py       # NEW: Agent service tests
├── requirements.txt                 # Updated with new dependencies
└── .env                             # Environment variables

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx                 # NEW: Chat page
│   └── layout.tsx                   # Existing layout
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx        # NEW: Main chat component
│   │   ├── MessageList.tsx          # NEW: Message display
│   │   └── MessageInput.tsx         # NEW: Input field
│   └── tasks/                       # Existing task components
├── lib/
│   ├── auth.ts                      # Better Auth config (existing)
│   └── api.ts                       # API client (existing, extended)
├── package.json                     # Updated with @openai/chatkit
└── .env.local                       # Environment variables
```

**Structure Decision**: Web application monorepo structure selected. Backend adds new chat route, MCP tools, agent service, and Gemini service. Frontend adds new chat page with OpenAI Chatkit components. Existing Phase 2 components (JWT middleware, Task model, DB connection, task routes) are reused without modification.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied by the proposed architecture.

---

## Phase 1 Artifacts Summary

### Completed Deliverables

1. **research.md** ✅
   - Resolved 8 technical unknowns
   - Documented 3 architectural decisions (ADRs)
   - Identified technology stack and dependencies
   - Defined implementation risks and mitigations

2. **data-model.md** ✅
   - Defined 2 new entities (Conversation, Message)
   - Documented relationships with existing entities (User, Task)
   - Created database migration script
   - Defined query patterns and performance estimates

3. **contracts/chat-api.yaml** ✅
   - OpenAPI 3.0 specification for POST /api/v1/chat
   - Request/response schemas with examples
   - Error response documentation
   - HTTP status code definitions

4. **contracts/mcp-tools.md** ✅
   - 5 MCP tool definitions with Gemini function schemas
   - Input/output contracts for each tool
   - Multi-step tool call patterns
   - Security and testing considerations

5. **quickstart.md** ✅
   - Environment setup instructions
   - Installation steps for dependencies
   - Database migration guide
   - Development workflow and testing strategy
   - Troubleshooting guide

### Key Decisions Made

1. **Use Gemini API directly** instead of OpenAI Agents SDK (not compatible)
2. **Use @chatscope/chat-ui-kit-react** instead of OpenAI Chatkit (not available)
3. **Custom agent loop implementation** for Gemini function calling
4. **Last 20 messages** loaded per request for conversation context
5. **User ID injection** at agent service layer from JWT token

### Architecture Highlights

- **Stateless backend**: All conversation state in Neon DB
- **Two-phase agent loop**: Gemini call → tool execution → Gemini call → response
- **User isolation**: All queries filtered by user_id from JWT
- **Reuse Phase 2**: JWT middleware, Task model, DB connection unchanged
- **Performance optimized**: Database indexes for fast message retrieval

### Dependencies Added

**Backend**:
- `google-generativeai>=0.3.0` (Gemini API)
- `python-jose[cryptography]>=3.3.0` (JWT verification)

**Frontend**:
- `@chatscope/chat-ui-kit-react@^2.0.0` (Chat UI)
- `@chatscope/chat-ui-kit-styles@^1.4.0` (Chat UI styles)

### Next Steps

1. Run `/sp.tasks` to generate implementation tasks from this plan
2. Review tasks.md for TDD workflow (Red-Green-Refactor)
3. Begin implementation phase with user approval

---

## Planning Complete

**Branch**: 002-ai-chatbot  
**Plan File**: D:\TaskFlow2\specs\002-ai-chatbot\plan.md  
**Artifacts Generated**:
- research.md
- data-model.md
- contracts/chat-api.yaml
- contracts/mcp-tools.md
- quickstart.md

**Status**: ✅ Ready for Phase 2 (tasks.md generation)

**Command to proceed**: `/sp.tasks`
