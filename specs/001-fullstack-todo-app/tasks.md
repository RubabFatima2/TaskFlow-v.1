# Tasks: Full-Stack Todo Web Application

**Input**: Design documents from `/specs/001-fullstack-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per TDD requirement in constitution (Section II: Test-First Development - NON-NEGOTIABLE)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/app/`, `frontend/components/`, `frontend/tests/`
- **Shared**: `specs/001-fullstack-todo-app/`, `docker-compose.yml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure per plan.md (app/, tests/, alembic/)
- [X] T002 Create frontend directory structure per plan.md (app/, components/, lib/, hooks/, context/)
- [X] T003 [P] Initialize backend Python project with requirements.txt (FastAPI, SQLModel, python-jose, bcrypt, pytest)
- [X] T004 [P] Initialize frontend Next.js project with package.json (Next.js 16+, TypeScript, Tailwind CSS, Better Auth)
- [X] T005 [P] Create backend/.env.example with required environment variables (DATABASE_URL, BETTER_AUTH_SECRET, JWT_ALGORITHM, etc.)
- [X] T006 [P] Create frontend/.env.local.example with required environment variables (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL)
- [X] T007 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [X] T008 [P] Configure Tailwind CSS in frontend/tailwind.config.ts
- [X] T009 [P] Setup pytest configuration in backend/pytest.ini
- [X] T010 [P] Create docker-compose.yml for local development (optional, for local PostgreSQL if not using Neon directly)
- [X] T011 [P] Create .gitignore files for backend/ and frontend/ (exclude .env, node_modules, __pycache__, etc.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [X] T012 Create backend/app/config.py for environment configuration management using Pydantic BaseSettings
- [X] T013 Create backend/app/database.py with async SQLModel engine and session management for Neon PostgreSQL
- [X] T014 Create backend/app/main.py with FastAPI app initialization, CORS middleware, and health check endpoint
- [X] T015 [P] Create backend/app/utils/security.py with password hashing (bcrypt) and JWT token generation/verification functions
- [X] T016 [P] Create backend/app/utils/dependencies.py with FastAPI dependency injection functions (get_db_session, get_current_user)
- [X] T017 Initialize Alembic in backend/alembic/ for database migrations
- [X] T018 Create initial Alembic migration for users and tasks tables in backend/alembic/versions/001_create_users_and_tasks.py
- [X] T019 Create backend/app/middleware/jwt_auth.py for JWT verification middleware
- [X] T020 [P] Create backend/app/models/__init__.py as package initializer
- [X] T021 [P] Create backend/app/schemas/__init__.py as package initializer
- [X] T022 [P] Create backend/app/routes/__init__.py as package initializer
- [X] T023 [P] Create backend/app/services/__init__.py as package initializer

### Frontend Foundation

- [X] T024 Create frontend/lib/auth.ts with Better Auth configuration (JWT plugin enabled)
- [X] T025 Create frontend/lib/api-client.ts with API client that automatically attaches JWT tokens from cookies
- [X] T026 Create frontend/lib/types.ts with TypeScript interfaces for User and Task entities
- [X] T027 Create frontend/context/AuthContext.tsx with authentication state management (user, isAuthenticated, login, logout, register)
- [X] T028 Create frontend/app/layout.tsx as root layout with AuthContext provider
- [X] T029 Create frontend/app/page.tsx as landing page with links to login/register
- [X] T030 [P] Create frontend/components/ui/Button.tsx as reusable button component
- [X] T031 [P] Create frontend/components/ui/Input.tsx as reusable input component
- [X] T032 [P] Create frontend/components/ui/Modal.tsx as reusable modal component

### Testing Foundation

- [X] T033 [P] Create backend/tests/conftest.py with pytest fixtures (test database, test client, test user)
- [X] T034 [P] Create frontend/tests/setup.ts with Jest and React Testing Library configuration

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts and securely log in to access their personal todo lists

**Independent Test**: Register a new user, log in, receive JWT token, verify token grants access to protected endpoints

### Tests for User Story 1 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T035 [P] [US1] Unit test for password hashing in backend/tests/unit/test_security.py
- [ ] T036 [P] [US1] Unit test for JWT token generation and verification in backend/tests/unit/test_security.py
- [ ] T037 [P] [US1] Unit test for user creation in backend/tests/unit/test_auth_service.py
- [ ] T038 [P] [US1] Unit test for user login in backend/tests/unit/test_auth_service.py
- [ ] T039 [P] [US1] Integration test for POST /api/v1/auth/register endpoint in backend/tests/integration/test_auth_routes.py
- [ ] T040 [P] [US1] Integration test for POST /api/v1/auth/login endpoint in backend/tests/integration/test_auth_routes.py
- [ ] T041 [P] [US1] Integration test for POST /api/v1/auth/refresh endpoint in backend/tests/integration/test_auth_routes.py
- [ ] T042 [P] [US1] Integration test for POST /api/v1/auth/logout endpoint in backend/tests/integration/test_auth_routes.py
- [ ] T043 [P] [US1] Integration test for GET /api/v1/auth/me endpoint in backend/tests/integration/test_auth_routes.py

### Backend Implementation for User Story 1

- [X] T044 [US1] Create User model in backend/app/models/user.py with SQLModel (id, email, password_hash, created_at, updated_at)
- [X] T045 [P] [US1] Create UserRegister schema in backend/app/schemas/auth.py (email, password validation)
- [X] T046 [P] [US1] Create UserLogin schema in backend/app/schemas/auth.py
- [X] T047 [P] [US1] Create UserResponse schema in backend/app/schemas/auth.py (no password_hash)
- [X] T048 [P] [US1] Create TokenResponse schema in backend/app/schemas/auth.py
- [X] T049 [US1] Implement AuthService in backend/app/services/auth_service.py (register_user, authenticate_user, create_tokens, verify_token)
- [X] T050 [US1] Implement POST /api/v1/auth/register endpoint in backend/app/routes/auth.py
- [X] T051 [US1] Implement POST /api/v1/auth/login endpoint in backend/app/routes/auth.py (set HTTP-only cookie)
- [X] T052 [US1] Implement POST /api/v1/auth/refresh endpoint in backend/app/routes/auth.py
- [X] T053 [US1] Implement POST /api/v1/auth/logout endpoint in backend/app/routes/auth.py (clear cookie)
- [X] T054 [US1] Implement GET /api/v1/auth/me endpoint in backend/app/routes/auth.py (requires authentication)
- [X] T055 [US1] Register auth routes in backend/app/main.py

### Frontend Implementation for User Story 1

- [X] T056 [P] [US1] Create useAuth hook in frontend/hooks/useAuth.ts (login, logout, register functions)
- [X] T057 [P] [US1] Create RegisterForm component in frontend/components/auth/RegisterForm.tsx
- [X] T058 [P] [US1] Create LoginForm component in frontend/components/auth/LoginForm.tsx
- [X] T059 [US1] Create register page in frontend/app/(auth)/register/page.tsx
- [X] T060 [US1] Create login page in frontend/app/(auth)/login/page.tsx
- [X] T061 [US1] Add authentication middleware in frontend/middleware.ts to protect dashboard routes

### Frontend Tests for User Story 1

- [ ] T062 [P] [US1] Component test for RegisterForm in frontend/tests/component/RegisterForm.test.tsx
- [ ] T063 [P] [US1] Component test for LoginForm in frontend/tests/component/LoginForm.test.tsx
- [ ] T064 [US1] E2E test for registration and login flow in frontend/tests/e2e/auth.spec.ts

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and receive JWT tokens

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks and view their personal task list

**Independent Test**: Log in, create multiple tasks with different properties, verify they appear in the user's task list (but not in other users' lists)

### Tests for User Story 2 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T065 [P] [US2] Unit test for task creation in backend/tests/unit/test_task_service.py
- [ ] T066 [P] [US2] Unit test for getting user tasks in backend/tests/unit/test_task_service.py
- [ ] T067 [P] [US2] Unit test for getting single task with ownership check in backend/tests/unit/test_task_service.py
- [ ] T068 [P] [US2] Integration test for POST /api/v1/tasks endpoint in backend/tests/integration/test_task_routes.py
- [ ] T069 [P] [US2] Integration test for GET /api/v1/tasks endpoint in backend/tests/integration/test_task_routes.py
- [ ] T070 [P] [US2] Integration test for GET /api/v1/tasks/{task_id} endpoint in backend/tests/integration/test_task_routes.py
- [ ] T071 [P] [US2] Integration test for user data isolation (user cannot see other users' tasks) in backend/tests/integration/test_task_routes.py

### Backend Implementation for User Story 2

- [X] T072 [US2] Create Task model in backend/app/models/task.py with SQLModel (id, user_id, title, description, completed, created_at, updated_at)
- [X] T073 [P] [US2] Create TaskCreate schema in backend/app/schemas/task.py (title 1-200 chars, optional description)
- [X] T074 [P] [US2] Create TaskResponse schema in backend/app/schemas/task.py
- [X] T075 [P] [US2] Create TaskListResponse schema in backend/app/schemas/task.py
- [X] T076 [US2] Implement TaskService in backend/app/services/task_service.py (create_task, get_user_tasks, get_task_by_id with ownership check)
- [X] T077 [US2] Implement POST /api/v1/tasks endpoint in backend/app/routes/tasks.py (extract user_id from JWT)
- [X] T078 [US2] Implement GET /api/v1/tasks endpoint in backend/app/routes/tasks.py (filter by authenticated user_id)
- [X] T079 [US2] Implement GET /api/v1/tasks/{task_id} endpoint in backend/app/routes/tasks.py (verify ownership, return 403 if not owner)
- [X] T080 [US2] Register task routes in backend/app/main.py

### Frontend Implementation for User Story 2

- [X] T081 [P] [US2] Create useTasks hook in frontend/hooks/useTasks.ts (fetchTasks, createTask functions)
- [X] T082 [P] [US2] Create TaskList component in frontend/components/tasks/TaskList.tsx
- [X] T083 [P] [US2] Create TaskItem component in frontend/components/tasks/TaskItem.tsx
- [X] T084 [P] [US2] Create TaskForm component in frontend/components/tasks/TaskForm.tsx (for creating new tasks)
- [ ] T085 [P] [US2] Create TaskDetail component in frontend/components/tasks/TaskDetail.tsx
- [X] T086 [US2] Create tasks list page in frontend/app/(dashboard)/tasks/page.tsx
- [ ] T087 [US2] Create task detail page in frontend/app/(dashboard)/tasks/[id]/page.tsx

### Frontend Tests for User Story 2

- [ ] T088 [P] [US2] Component test for TaskList in frontend/tests/component/TaskList.test.tsx
- [ ] T089 [P] [US2] Component test for TaskForm in frontend/tests/component/TaskForm.test.tsx
- [ ] T090 [US2] E2E test for creating and viewing tasks in frontend/tests/e2e/tasks.spec.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can register, login, create tasks, and view their task list

---

## Phase 5: User Story 3 - Mark Tasks as Complete/Incomplete (Priority: P1) 🎯 MVP

**Goal**: Users can mark tasks as complete or incomplete to track their progress

**Independent Test**: Create a task, toggle its completed status between true and false, verify the status persists correctly

### Tests for User Story 3 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T091 [P] [US3] Unit test for updating task completed status in backend/tests/unit/test_task_service.py
- [ ] T092 [P] [US3] Integration test for PUT /api/v1/tasks/{task_id} endpoint (toggle completed) in backend/tests/integration/test_task_routes.py
- [ ] T093 [P] [US3] Integration test for ownership check when updating task in backend/tests/integration/test_task_routes.py (return 403 if not owner)

### Backend Implementation for User Story 3

- [X] T094 [P] [US3] Create TaskUpdate schema in backend/app/schemas/task.py (optional title, description, completed)
- [X] T095 [US3] Add update_task method to TaskService in backend/app/services/task_service.py (with ownership check)
- [X] T096 [US3] Implement PUT /api/v1/tasks/{task_id} endpoint in backend/app/routes/tasks.py (verify ownership, return 403 if not owner)

### Frontend Implementation for User Story 3

- [X] T097 [US3] Add toggleTaskCompleted function to useTasks hook in frontend/hooks/useTasks.ts
- [X] T098 [US3] Add checkbox/button to TaskItem component in frontend/components/tasks/TaskItem.tsx for toggling completed status
- [X] T099 [US3] Add optimistic UI update for task completion in frontend/components/tasks/TaskItem.tsx

### Frontend Tests for User Story 3

- [ ] T100 [P] [US3] Component test for task completion toggle in frontend/tests/component/TaskItem.test.tsx
- [ ] T101 [US3] E2E test for marking tasks complete/incomplete in frontend/tests/e2e/tasks.spec.ts

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - users can register, login, create tasks, view tasks, and mark them complete/incomplete

---

## Phase 6: User Story 4 - Edit and Delete Tasks (Priority: P2)

**Goal**: Users can modify task details and remove tasks they no longer need

**Independent Test**: Create a task, edit its properties, verify changes persist, then delete the task and confirm it no longer appears

### Tests for User Story 4 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T102 [P] [US4] Unit test for updating task title and description in backend/tests/unit/test_task_service.py
- [ ] T103 [P] [US4] Unit test for deleting task in backend/tests/unit/test_task_service.py
- [ ] T104 [P] [US4] Integration test for PUT /api/v1/tasks/{task_id} endpoint (update title/description) in backend/tests/integration/test_task_routes.py
- [ ] T105 [P] [US4] Integration test for DELETE /api/v1/tasks/{task_id} endpoint in backend/tests/integration/test_task_routes.py
- [ ] T106 [P] [US4] Integration test for ownership check when deleting task in backend/tests/integration/test_task_routes.py (return 403 if not owner)

### Backend Implementation for User Story 4

- [ ] T107 [US4] Add delete_task method to TaskService in backend/app/services/task_service.py (with ownership check)
- [X] T108 [US4] Implement DELETE /api/v1/tasks/{task_id} endpoint in backend/app/routes/tasks.py (verify ownership, return 403 if not owner)

### Frontend Implementation for User Story 4

- [X] T109 [US4] Add updateTask and deleteTask functions to useTasks hook in frontend/hooks/useTasks.ts
- [X] T110 [US4] Add edit mode to TaskForm component in frontend/components/tasks/TaskForm.tsx (support both create and edit)
- [X] T111 [US4] Add edit and delete buttons to TaskItem component in frontend/components/tasks/TaskItem.tsx
- [X] T112 [US4] Add confirmation modal for task deletion in frontend/components/tasks/TaskItem.tsx

### Frontend Tests for User Story 4

- [ ] T113 [P] [US4] Component test for task editing in frontend/tests/component/TaskForm.test.tsx
- [ ] T114 [P] [US4] Component test for task deletion in frontend/tests/component/TaskItem.test.tsx
- [ ] T115 [US4] E2E test for editing and deleting tasks in frontend/tests/e2e/tasks.spec.ts

**Checkpoint**: All P1 and P2 user stories should now be independently functional - full CRUD operations on tasks

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T116 [P] Add loading states to all frontend components (Button, TaskList, TaskForm)
- [ ] T117 [P] Add error handling and user-friendly error messages across frontend
- [ ] T118 [P] Add toast notifications for success/error messages in frontend
- [ ] T119 [P] Implement form validation with inline error messages in frontend
- [ ] T120 [P] Add accessibility attributes (ARIA labels, keyboard navigation) to frontend components
- [ ] T121 [P] Add rate limiting middleware to backend API endpoints (5 req/min for auth, 30 req/min for tasks)
- [ ] T122 [P] Add request logging middleware to backend
- [ ] T123 [P] Add error tracking integration (Sentry or similar) to backend and frontend
- [ ] T124 [P] Optimize database queries with proper indexes (verify indexes from migration)
- [ ] T125 [P] Add API response caching headers where appropriate
- [ ] T126 [P] Run security audit (npm audit, pip-audit)
- [ ] T127 [P] Update README.md with setup instructions
- [ ] T128 [P] Verify all tests pass and coverage meets requirements (70% minimum, 100% for auth/persistence)
- [ ] T129 Run quickstart.md validation (follow all steps, verify application works end-to-end)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 3 (P1): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 4 (P2): Can start after Foundational - No dependencies on other stories (independent)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before services
- Services before routes/endpoints
- Backend implementation before frontend implementation (API-first)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models/schemas within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for User Story 1 together:
Task: "Unit test for password hashing in backend/tests/unit/test_security.py"
Task: "Unit test for JWT token generation in backend/tests/unit/test_security.py"
Task: "Unit test for user creation in backend/tests/unit/test_auth_service.py"

# Launch all integration tests for User Story 1 together:
Task: "Integration test for POST /api/v1/auth/register in backend/tests/integration/test_auth_routes.py"
Task: "Integration test for POST /api/v1/auth/login in backend/tests/integration/test_auth_routes.py"
Task: "Integration test for POST /api/v1/auth/refresh in backend/tests/integration/test_auth_routes.py"

# Launch all schemas for User Story 1 together:
Task: "Create UserRegister schema in backend/app/schemas/auth.py"
Task: "Create UserLogin schema in backend/app/schemas/auth.py"
Task: "Create UserResponse schema in backend/app/schemas/auth.py"
Task: "Create TokenResponse schema in backend/app/schemas/auth.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Create/View Tasks)
5. Complete Phase 5: User Story 3 (Mark Complete)
6. **STOP and VALIDATE**: Test all three stories independently
7. Deploy/demo if ready - this is the MVP!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Auth working!)
3. Add User Story 2 → Test independently → Deploy/Demo (Can create/view tasks!)
4. Add User Story 3 → Test independently → Deploy/Demo (Can mark complete - MVP!)
5. Add User Story 4 → Test independently → Deploy/Demo (Full CRUD!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Create/View Tasks) - can work in parallel with A
   - Developer C: User Story 3 (Mark Complete) - can work in parallel with A and B
3. Stories complete and integrate independently

---

## Summary

- **Total Tasks**: 129
- **User Story 1 (Authentication)**: 30 tasks (T035-T064)
- **User Story 2 (Create/View Tasks)**: 26 tasks (T065-T090)
- **User Story 3 (Mark Complete)**: 11 tasks (T091-T101)
- **User Story 4 (Edit/Delete)**: 14 tasks (T102-T115)
- **Setup**: 11 tasks (T001-T011)
- **Foundational**: 23 tasks (T012-T034)
- **Polish**: 14 tasks (T116-T129)

**MVP Scope**: User Stories 1, 2, 3 (67 tasks including setup and foundational)

**Parallel Opportunities**: 78 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Register user, login, receive JWT, access protected endpoint
- US2: Create tasks, view task list, verify user isolation
- US3: Toggle task completed status, verify persistence
- US4: Edit task properties, delete task, verify removal

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD enforced: Write tests first, ensure they fail, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow constitution requirements: 70% coverage minimum, 100% for auth and persistence
