# Implementation Plan: Full-Stack Todo Web Application

**Branch**: `001-fullstack-todo-app` | **Date**: 2026-04-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fullstack-todo-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a multi-user full-stack todo web application with Next.js 16+ frontend and FastAPI backend, using Better Auth + JWT for authentication and Neon Serverless PostgreSQL for data persistence. The application provides CRUD operations on tasks with user-level data isolation, ensuring each user can only access their own tasks. Core features include user registration/login, task creation/viewing, marking tasks complete/incomplete, and task editing/deletion.

## Technical Context

**Language/Version**: 
- Frontend: TypeScript 5.x (strict mode) with Next.js 16+
- Backend: Python 3.11+

**Primary Dependencies**: 
- Frontend: Next.js 16+ (App Router), Better Auth (JWT plugin), Tailwind CSS, React 19+
- Backend: FastAPI 0.110+, SQLModel 0.0.14+, Pydantic 2.x, python-jose[cryptography] or PyJWT, bcrypt or argon2-cffi

**Storage**: Neon Serverless PostgreSQL (connection pooling built-in)

**Testing**: 
- Frontend: Jest + React Testing Library for unit/component tests, Playwright for E2E
- Backend: pytest + pytest-asyncio for unit/integration tests

**Target Platform**: 
- Frontend: Modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Backend: Linux server (containerized with Docker)

**Project Type**: Web application (monorepo with frontend/ and backend/ directories)

**Performance Goals**: 
- API endpoints: <200ms for simple queries, <1s for complex operations
- Page load: <2s initial, <500ms subsequent navigation
- Database queries: <100ms for indexed queries
- UI interactions: <100ms perceived response time

**Constraints**: 
- 100% user data isolation (users can only access their own tasks)
- Zero password/token leaks in logs
- JWT tokens in HTTP-only cookies with Secure and SameSite=Strict flags
- Shared secret BETTER_AUTH_SECRET must be identical in frontend and backend
- All API inputs validated with Pydantic schemas
- TDD mandatory: 70% code coverage minimum, 100% for auth and data persistence

**Scale/Scope**: 
- MVP: 100 concurrent users without performance degradation
- Task schema: 7 fields (id, user_id, title, description, completed, created_at, updated_at)
- User schema: 5 fields (id, email, password_hash, created_at, updated_at)
- 5 core user stories (registration/login, create/view tasks, mark complete, edit/delete, filter/sort - P3 future)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Technology Stack Compliance
- **Next.js 16+ (App Router)**: ✅ Specified in spec
- **TypeScript (strict mode)**: ✅ Specified in spec
- **Tailwind CSS**: ✅ Specified in spec
- **FastAPI**: ✅ Specified in spec
- **SQLModel**: ✅ Specified in spec
- **Neon Serverless PostgreSQL**: ✅ Specified in spec
- **Better Auth + JWT**: ✅ Specified in spec with BETTER_AUTH_SECRET

### ✅ Authentication & Authorization (Section VII)
- **Better Auth Integration**: ✅ JWT plugin enabled, shared secret BETTER_AUTH_SECRET
- **JWT Token Structure**: ✅ user_id, email, exp, iat claims (FR-006)
- **Token Expiration**: ✅ 15-minute access, 7-day refresh (FR-007)
- **User-Level Data Isolation**: ✅ Enforced in all queries (FR-009, FR-019)
- **Token Storage**: ✅ HTTP-only cookies with Secure and SameSite=Strict (FR-020)
- **User ID from JWT**: ✅ Extract from token, not URL path (FR-023)

### ✅ Test-First Development (Section II)
- **TDD Mandatory**: ✅ Tests written before implementation
- **Coverage Requirements**: ✅ 70% minimum, 100% for auth and persistence
- **Red-Green-Refactor**: ✅ Enforced in workflow

### ✅ Security by Default (Section III)
- **Password Hashing**: ✅ bcrypt or Argon2 (FR-003)
- **Input Validation**: ✅ Pydantic schemas on all inputs (FR-010)
- **Parameterized Queries**: ✅ SQLModel ORM prevents SQL injection
- **No Sensitive Data Logging**: ✅ Zero password/token leaks (SC-007)
- **Environment Variables**: ✅ All secrets in .env (FR-018)

### ✅ API-First Architecture (Section IV)
- **RESTful Conventions**: ✅ GET, POST, PUT, DELETE
- **Versioned URLs**: ✅ /api/v1/resource pattern
- **User ID from JWT**: ✅ Not in URL path (FR-023)
- **HTTP Status Codes**: ✅ 200, 201, 400, 401, 403, 404, 409, 500, 503 (FR-017)
- **JSON Request/Response**: ✅ Pydantic schemas

### ✅ Data Model Alignment (Architecture Standards)
- **User Entity**: ✅ id, email, password_hash, created_at, updated_at
- **Task Entity**: ✅ id, user_id, title (1-200 chars), description, completed (boolean), created_at, updated_at
- **Foreign Key Constraints**: ✅ task.user_id → user.id
- **Indexes**: ✅ user_id, completed, created_at

### ✅ Spec-Driven Development Workflow (Section XIV)
- **Specification Phase**: ✅ spec.md complete and approved
- **Planning Phase**: ✅ In progress (this document)
- **Task Generation Phase**: ⏳ Next step after plan approval
- **Implementation Phase**: ⏳ After tasks approved

### ✅ Performance Standards
- **API Response Time**: ✅ <200ms simple, <1s complex
- **Page Load Time**: ✅ <2s initial, <500ms subsequent
- **Database Queries**: ✅ <100ms indexed
- **UI Interactions**: ✅ <100ms perceived

### ✅ Monorepo Structure
- **Frontend Directory**: ✅ frontend/ with Next.js
- **Backend Directory**: ✅ backend/ with FastAPI
- **Specs Directory**: ✅ specs/001-fullstack-todo-app/
- **Docker Compose**: ✅ docker-compose.yml for local dev

### Gate Status: ✅ PASS
All constitutional requirements are met. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-fullstack-todo-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   ├── auth.yaml        # Authentication endpoints
│   └── tasks.yaml       # Task CRUD endpoints
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
TaskFlow2/
├── frontend/                    # Next.js 16+ application
│   ├── app/                     # Next.js App Router
│   │   ├── (auth)/              # Auth route group
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/         # Protected route group
│   │   │   └── tasks/
│   │   │       ├── page.tsx     # Task list
│   │   │       └── [id]/
│   │   │           └── page.tsx # Task detail
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Landing page
│   ├── components/              # React components
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskDetail.tsx
│   │   └── ui/                  # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       └── Modal.tsx
│   ├── lib/                     # Utilities and services
│   │   ├── auth.ts              # Better Auth configuration
│   │   ├── api-client.ts        # API client with JWT attachment
│   │   └── types.ts             # TypeScript types
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts
│   │   └── useTasks.ts
│   ├── context/                 # React Context providers
│   │   └── AuthContext.tsx
│   ├── public/                  # Static assets
│   ├── tests/                   # Frontend tests
│   │   ├── unit/
│   │   ├── component/
│   │   └── e2e/
│   ├── .env.local               # Frontend environment variables
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connection and session
│   │   ├── models/              # SQLModel models
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User model
│   │   │   └── task.py          # Task model
│   │   ├── schemas/             # Pydantic schemas (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Auth schemas
│   │   │   └── task.py          # Task schemas
│   │   ├── routes/              # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # /api/v1/auth/*
│   │   │   └── tasks.py         # /api/v1/tasks/*
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Authentication logic
│   │   │   └── task_service.py  # Task CRUD logic
│   │   ├── middleware/          # Middleware
│   │   │   ├── __init__.py
│   │   │   └── jwt_auth.py      # JWT verification middleware
│   │   └── utils/               # Utilities
│   │       ├── __init__.py
│   │       ├── security.py      # Password hashing, JWT utils
│   │       └── dependencies.py  # FastAPI dependencies
│   ├── tests/                   # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py          # pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_auth_service.py
│   │   │   └── test_task_service.py
│   │   └── integration/
│   │       ├── test_auth_routes.py
│   │       └── test_task_routes.py
│   ├── alembic/                 # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── .env                     # Backend environment variables
│   ├── requirements.txt         # Python dependencies
│   ├── pyproject.toml           # Python project config
│   └── pytest.ini               # pytest configuration
│
├── .specify/                    # Spec-Kit Plus configuration
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   └── scripts/
├── specs/                       # Feature specifications
│   └── 001-fullstack-todo-app/
├── docker-compose.yml           # Local development setup
├── .gitignore
├── CLAUDE.md                    # Root project instructions
├── AGENTS.md                    # Agent configuration
└── README.md
```

**Structure Decision**: Web application monorepo structure selected. Frontend and backend are separate applications that communicate via REST API. This structure supports:
- Independent deployment of frontend and backend
- Clear separation of concerns
- Technology-specific tooling in each directory
- Shared specifications in specs/ directory
- Docker Compose for local development with Neon PostgreSQL connection

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional requirements are met without exceptions.
