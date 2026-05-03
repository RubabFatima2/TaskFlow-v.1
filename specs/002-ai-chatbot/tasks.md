# Tasks: AI-Powered Todo Chatbot (Phase 3)

**Input**: Design documents from `/specs/002-ai-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT included in this implementation as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/app/`, `frontend/components/`
- Paths follow monorepo structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Install backend dependencies: `google-generativeai==0.3.2` in backend/requirements.txt
- [ ] T002 [P] Install frontend dependencies: `@chatscope/chat-ui-kit-react@^2.0.0` and `@chatscope/chat-ui-kit-styles@^1.4.0` in frontend/package.json
- [ ] T003 [P] Add environment variables to backend/.env: GEMINI_API_KEY, GEMINI_MODEL
- [ ] T004 [P] Create backend/app/mcp/ directory with __init__.py
- [ ] T005 [P] Create backend/app/services/ directory with __init__.py
- [ ] T006 [P] Create frontend/components/chat/ directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create Conversation model in backend/app/models/conversation.py with SQLModel schema (id, user_id, created_at, updated_at, relationships)
- [ ] T008 [P] Create Message model in backend/app/models/message.py with SQLModel schema (id, conversation_id, user_id, role, content, created_at, relationships)
- [ ] T009 Create Alembic migration 002_add_conversation_message_tables.py in backend/alembic/versions/ with tables, indexes, and foreign keys from data-model.md
- [ ] T010 Run Alembic migration: `alembic upgrade head` and verify conversations and messages tables created
- [ ] T011 Create Gemini service wrapper in backend/app/services/gemini_service.py with async client initialization, generate_content method, and error handling
- [ ] T012 [P] Create MCP tool schemas in backend/app/mcp/schemas.py with Pydantic models for all 5 tools (AddTaskInput, ListTasksInput, CompleteTaskInput, UpdateTaskInput, DeleteTaskInput)
- [ ] T013 Create MCP tools implementation in backend/app/mcp/tools.py with all 5 async functions (add_task, list_tasks, complete_task, update_task, delete_task) that reuse existing Task model
- [ ] T014 Create agent service in backend/app/services/agent_service.py with custom agent loop (load history, call Gemini, execute tools, call Gemini again, return response)
- [ ] T015 Create chat endpoint in backend/app/routes/chat.py with POST /api/v1/chat route, JWT authentication dependency, request/response models, and error handling
- [ ] T016 Register chat route in backend/app/main.py by importing and including chat router

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks by typing natural language messages like "add buy groceries"

**Independent Test**: Send chat message "add buy milk" and verify new task appears in user's task list with title "buy milk"

### Implementation for User Story 1

- [ ] T017 [US1] Implement add_task tool logic in backend/app/mcp/tools.py: validate inputs, create Task instance, save to DB, return success response with task data
- [ ] T018 [US1] Add add_task tool to agent service tool registry in backend/app/services/agent_service.py with Gemini function schema from contracts/mcp-tools.md
- [ ] T019 [US1] Implement conversation creation logic in backend/app/routes/chat.py: create new Conversation when conversation_id is None
- [ ] T020 [US1] Implement message persistence in backend/app/routes/chat.py: save user message and assistant message to messages table after agent response
- [ ] T021 [US1] Add user_id injection logic in backend/app/services/agent_service.py: inject user_id from JWT into all tool calls before execution
- [ ] T022 [US1] Add error handling for Gemini API failures in backend/app/services/gemini_service.py: catch ResourceExhausted (429), ServiceUnavailable (503), TimeoutError (504), and generic exceptions with appropriate HTTP responses
- [ ] T023 [US1] Add input validation in backend/app/routes/chat.py: validate message length (1-5000 chars), conversation_id format (UUID), return 400 for validation errors

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - View Tasks via Conversation (Priority: P1)

**Goal**: Enable users to view tasks by asking questions like "show my tasks" or "what do I need to do today?"

**Independent Test**: Create a few tasks, then send "show my tasks" and verify chatbot returns formatted list of all tasks

### Implementation for User Story 2

- [ ] T024 [US2] Implement list_tasks tool logic in backend/app/mcp/tools.py: query tasks by user_id, filter by status (all/pending/completed), return tasks array with count
- [ ] T025 [US2] Add list_tasks tool to agent service tool registry in backend/app/services/agent_service.py with Gemini function schema including status filter enum
- [ ] T026 [US2] Implement conversation history loading in backend/app/routes/chat.py: query last 20 messages ordered by created_at DESC, reverse to chronological order
- [ ] T027 [US2] Add conversation history to agent service context in backend/app/services/agent_service.py: format messages as Gemini conversation history with roles (user/assistant)
- [ ] T028 [US2] Add conversation ownership verification in backend/app/routes/chat.py: verify conversation.user_id matches JWT user_id, return 403 if mismatch

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create and view tasks

---

## Phase 5: User Story 3 - Mark Tasks Complete via Chat (Priority: P2)

**Goal**: Enable users to mark tasks as done by saying "done with groceries" or "mark buy milk as complete"

**Independent Test**: Create task "buy milk", send "mark buy milk as complete", verify task status changes to completed

### Implementation for User Story 3

- [ ] T029 [US3] Implement complete_task tool logic in backend/app/mcp/tools.py: find task by task_id, verify ownership, set completed=True, update updated_at, return success response
- [ ] T030 [US3] Add complete_task tool to agent service tool registry in backend/app/services/agent_service.py with Gemini function schema
- [ ] T031 [US3] Implement multi-step tool call pattern in backend/app/services/agent_service.py: enable agent to call list_tasks first to find task_id, then call complete_task with found task_id
- [ ] T032 [US3] Add task matching logic guidance in tool descriptions: update list_tasks and complete_task descriptions to guide Gemini on matching task titles to IDs

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently - users can create, view, and complete tasks

---

## Phase 6: User Story 4 - Update Task Details via Chat (Priority: P3)

**Goal**: Enable users to modify tasks by saying "change groceries to buy milk and bread"

**Independent Test**: Create task "groceries", send "change groceries to buy milk and eggs", verify task title updates

### Implementation for User Story 4

- [ ] T033 [US4] Implement update_task tool logic in backend/app/mcp/tools.py: find task by task_id, verify ownership, update title and/or description, validate at least one field provided, return updated task
- [ ] T034 [US4] Add update_task tool to agent service tool registry in backend/app/services/agent_service.py with Gemini function schema including optional title and description parameters
- [ ] T035 [US4] Add validation for update_task in backend/app/mcp/tools.py: ensure at least one of title or description is provided, return error if both are None

**Checkpoint**: User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Delete Tasks via Chat (Priority: P3)

**Goal**: Enable users to remove tasks by saying "delete groceries" or "remove the dentist task"

**Independent Test**: Create task "test task", send "delete test task", verify it no longer appears in task list

### Implementation for User Story 5

- [ ] T036 [US5] Implement delete_task tool logic in backend/app/mcp/tools.py: find task by task_id, verify ownership, delete from database, return success message
- [ ] T037 [US5] Add delete_task tool to agent service tool registry in backend/app/services/agent_service.py with Gemini function schema

**Checkpoint**: User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Persistent Conversation Context (Priority: P2)

**Goal**: Enable chatbot to remember conversation history across sessions

**Independent Test**: Have a conversation, close session, reopen, verify chatbot remembers previous context (last 20 messages)

### Implementation for User Story 6

- [ ] T038 [US6] Add conversation updated_at timestamp update in backend/app/routes/chat.py: update conversation.updated_at whenever new message is added
- [ ] T039 [US6] Implement conversation retrieval endpoint (optional) in backend/app/routes/chat.py: GET /api/v1/conversations to list user's conversations ordered by updated_at DESC
- [ ] T040 [US6] Add conversation_id persistence in frontend chat component: store conversation_id in component state and include in all subsequent requests

**Checkpoint**: Conversation history persists across sessions

---

## Phase 9: User Story 7 - Multi-Turn Conversation Flow (Priority: P2)

**Goal**: Enable natural back-and-forth conversations where chatbot asks clarifying questions

**Independent Test**: Send ambiguous command "add task", verify chatbot asks "What would you like the task to be?"

### Implementation for User Story 7

- [ ] T041 [US7] Add clarification response logic in backend/app/services/agent_service.py: when tool parameters are missing, return clarifying question instead of error
- [ ] T042 [US7] Implement ambiguous task reference handling in backend/app/services/agent_service.py: when multiple tasks match user's description, list options and ask user to choose
- [ ] T043 [US7] Add helpful guidance for unknown commands in backend/app/services/agent_service.py: when no tool matches user intent, return message explaining available commands

**Checkpoint**: All user stories should now be independently functional with natural conversation flow

---

## Phase 10: Frontend Chat UI (All User Stories)

**Purpose**: Build React chat interface for all user stories

- [ ] T044 [P] Create ChatInterface component in frontend/components/chat/ChatInterface.tsx: main container with @chatscope/chat-ui-kit-react components, state management for messages and conversation_id
- [ ] T045 [P] Create MessageList component in frontend/components/chat/MessageList.tsx: display message history with user/assistant roles, auto-scroll to bottom
- [ ] T046 [P] Create MessageInput component in frontend/components/chat/MessageInput.tsx: input field with send button, handle Enter key, disable during loading
- [ ] T047 Create chat page in frontend/app/chat/page.tsx: integrate ChatInterface component, handle authentication, fetch conversation history on mount
- [ ] T048 Import @chatscope/chat-ui-kit-styles in frontend/app/layout.tsx: add stylesheet import for chat UI components
- [ ] T049 Create API client function in frontend/lib/api.ts: sendChatMessage(conversationId, message) with JWT token in Authorization header
- [ ] T050 Add error handling in frontend/components/chat/ChatInterface.tsx: display error messages for 401 (re-auth), 403 (access denied), 503 (AI unavailable)
- [ ] T051 Add loading states in frontend/components/chat/ChatInterface.tsx: show typing indicator while waiting for AI response
- [ ] T052 Add navigation link to chat page in frontend/app/layout.tsx or navigation component

**Checkpoint**: Frontend chat UI complete and integrated with backend

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T053 [P] Add rate limiting for chat endpoint in backend/app/routes/chat.py: 30 requests per minute per user, return 429 with Retry-After header
- [ ] T054 [P] Add logging for all tool executions in backend/app/mcp/tools.py: log tool name, user_id, success/failure, execution time
- [ ] T055 [P] Add logging for Gemini API calls in backend/app/services/gemini_service.py: log request/response, token usage, latency
- [ ] T056 [P] Add CORS configuration in backend/app/main.py: allow frontend origin for chat endpoint
- [ ] T057 Optimize database queries in backend/app/routes/chat.py: add eager loading for conversation.messages relationship
- [ ] T058 Add conversation_id validation in backend/app/routes/chat.py: verify UUID format, return 400 for invalid format, return 404 for not found
- [ ] T059 Add accessibility attributes in frontend/components/chat/: ARIA labels for messages, keyboard navigation, screen reader support
- [ ] T060 Test complete workflow per quickstart.md manual testing checklist: verify all user stories work end-to-end
- [ ] T061 Update backend/requirements.txt with all dependencies: run `pip freeze > requirements.txt`
- [ ] T062 Update frontend/package.json with all dependencies: verify @chatscope packages are listed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Frontend (Phase 10)**: Can start after Foundational phase, works with any completed user story
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but benefits from US2 for task lookup)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but benefits from US2 for task lookup)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but benefits from US2 for task lookup)
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 7 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Models before services (T007-T008 before T011-T014)
- Services before endpoints (T011-T014 before T015)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T002, T003, T004, T005, T006 can run in parallel
- **Phase 2**: T008, T012 can run in parallel with T007
- **Phase 10**: T044, T045, T046 can run in parallel
- **Phase 11**: T053, T054, T055, T056 can run in parallel
- **User Stories**: Once Foundational phase completes, all user stories (Phase 3-9) can start in parallel if team capacity allows

---

## Parallel Example: Foundational Phase

```bash
# After T007 completes, launch these in parallel:
Task T008: "Create Message model in backend/app/models/message.py"
Task T012: "Create MCP tool schemas in backend/app/mcp/schemas.py"

# After T011-T014 complete, these can run in parallel:
Task T015: "Create chat endpoint in backend/app/routes/chat.py"
```

---

## Parallel Example: Frontend Phase

```bash
# Launch all frontend components in parallel:
Task T044: "Create ChatInterface component in frontend/components/chat/ChatInterface.tsx"
Task T045: "Create MessageList component in frontend/components/chat/MessageList.tsx"
Task T046: "Create MessageInput component in frontend/components/chat/MessageInput.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Natural Language Task Creation)
4. Complete Phase 4: User Story 2 (View Tasks via Conversation)
5. Complete Phase 10: Frontend Chat UI (basic version)
6. **STOP and VALIDATE**: Test User Stories 1 & 2 independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + User Story 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 (Complete tasks) → Test independently → Deploy/Demo
4. Add User Story 6 (Persistent context) → Test independently → Deploy/Demo
5. Add User Story 7 (Multi-turn) → Test independently → Deploy/Demo
6. Add User Story 4 & 5 (Update/Delete) → Test independently → Deploy/Demo
7. Complete Phase 11: Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + User Story 2 (P1 stories)
   - Developer B: User Story 3 + User Story 6 (P2 stories)
   - Developer C: Frontend Chat UI (Phase 10)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not requested in the specification
- All tasks reuse existing Phase 2 components (JWT middleware, Task model, DB connection)
- User ID is ALWAYS extracted from JWT token, never from request body
- All database queries MUST filter by user_id for data isolation
- Gemini API key stored in environment variable, never hardcoded
- Frontend uses @chatscope/chat-ui-kit-react (OpenAI Chatkit not publicly available)
- Backend uses custom agent loop (OpenAI Agents SDK not compatible with Gemini)

---

## Total Task Count

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 10 tasks (CRITICAL - blocks all user stories)
- **Phase 3 (US1)**: 7 tasks
- **Phase 4 (US2)**: 5 tasks
- **Phase 5 (US3)**: 4 tasks
- **Phase 6 (US4)**: 3 tasks
- **Phase 7 (US5)**: 2 tasks
- **Phase 8 (US6)**: 3 tasks
- **Phase 9 (US7)**: 3 tasks
- **Phase 10 (Frontend)**: 9 tasks
- **Phase 11 (Polish)**: 10 tasks

**Total**: 62 tasks

**MVP Scope (Recommended)**: Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 10 (basic) = ~30 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases
