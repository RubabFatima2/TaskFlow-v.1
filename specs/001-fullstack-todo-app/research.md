# Research: Full-Stack Todo Web Application

**Feature**: 001-fullstack-todo-app  
**Date**: 2026-04-10  
**Status**: Complete

## Overview

This document captures research findings, technical decisions, and best practices for implementing a full-stack todo application with Next.js 16+, FastAPI, and Neon Serverless PostgreSQL.

## Research Areas

### 1. Better Auth + FastAPI Integration

**Decision**: Use Better Auth (frontend) with JWT plugin + FastAPI JWT verification (backend) with shared secret

**Rationale**:
- Better Auth is a modern TypeScript authentication library designed for Next.js
- JWT tokens provide stateless authentication suitable for API-first architecture
- Shared secret (`BETTER_AUTH_SECRET`) enables independent verification on both sides
- HTTP-only cookies prevent XSS attacks while maintaining user sessions

**Implementation Approach**:
- Frontend: Configure Better Auth with JWT plugin, store tokens in HTTP-only cookies
- Backend: Implement JWT verification middleware using `python-jose[cryptography]` or `PyJWT`
- Shared secret must be identical in both `.env.local` (frontend) and `.env` (backend)
- Token payload includes: `user_id`, `email`, `exp` (expiration), `iat` (issued at)

**Alternatives Considered**:
- **Session-based auth with shared database**: Rejected - requires database coupling between frontend and backend
- **OAuth2 with external provider**: Rejected - adds complexity for MVP, can be added later
- **Custom JWT implementation**: Rejected - Better Auth provides battle-tested implementation

**References**:
- Better Auth documentation: https://www.better-auth.com/
- FastAPI JWT authentication: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

---

### 2. Next.js 16+ App Router Best Practices

**Decision**: Use App Router with route groups for authentication and protected routes

**Rationale**:
- App Router is the recommended approach for Next.js 16+
- Route groups `(auth)` and `(dashboard)` provide logical organization without affecting URLs
- Server Components by default improve performance
- Built-in loading and error states improve UX

**Implementation Approach**:
- `app/(auth)/login/page.tsx` - Login page (public)
- `app/(auth)/register/page.tsx` - Registration page (public)
- `app/(dashboard)/tasks/page.tsx` - Task list (protected)
- Use middleware for authentication checks on protected routes
- Server Components for data fetching, Client Components for interactivity

**Best Practices**:
- Use Server Actions for form submissions
- Implement loading.tsx and error.tsx for better UX
- Use React Suspense for streaming
- Optimize images with next/image
- Use TypeScript strict mode for type safety

**References**:
- Next.js App Router documentation: https://nextjs.org/docs/app
- Next.js authentication patterns: https://nextjs.org/docs/app/building-your-application/authentication

---

### 3. FastAPI + SQLModel Architecture

**Decision**: Use layered architecture with models, schemas, services, and routes

**Rationale**:
- Clear separation of concerns improves maintainability
- SQLModel combines SQLAlchemy ORM with Pydantic validation
- Service layer encapsulates business logic for easier testing
- Dependency injection pattern for database sessions

**Implementation Approach**:
- **Models** (`app/models/`): SQLModel classes for database tables
- **Schemas** (`app/schemas/`): Pydantic models for request/response validation
- **Services** (`app/services/`): Business logic (auth, task CRUD)
- **Routes** (`app/routes/`): FastAPI endpoints that call services
- **Middleware** (`app/middleware/`): JWT verification, CORS, error handling

**Best Practices**:
- Use async/await for database operations
- Implement dependency injection for database sessions
- Use Pydantic BaseSettings for configuration management
- Separate read and write schemas (e.g., TaskCreate, TaskRead, TaskUpdate)
- Use FastAPI's automatic OpenAPI documentation

**References**:
- FastAPI documentation: https://fastapi.tiangolo.com/
- SQLModel documentation: https://sqlmodel.tiangolo.com/

---

### 4. Neon Serverless PostgreSQL Connection Management

**Decision**: Use Neon's built-in connection pooling with SQLModel async engine

**Rationale**:
- Neon provides automatic connection pooling (no need for PgBouncer)
- Serverless-friendly with fast cold starts
- Supports PostgreSQL 15+ features
- Built-in branching for development/staging environments

**Implementation Approach**:
- Use `DATABASE_URL` environment variable with Neon connection string
- Configure SQLModel with async engine: `create_async_engine(DATABASE_URL)`
- Use connection pooling parameters: `pool_size=20, max_overflow=10`
- Implement health check endpoint to verify database connectivity

**Best Practices**:
- Use connection string format: `postgresql+asyncpg://user:pass@host/db`
- Enable SSL mode: `?sslmode=require`
- Set statement timeout to prevent long-running queries
- Use database migrations with Alembic
- Implement retry logic for transient connection failures

**References**:
- Neon documentation: https://neon.tech/docs
- SQLModel async engine: https://sqlmodel.tiangolo.com/tutorial/async/

---

### 5. JWT Token Security Best Practices

**Decision**: Use HTTP-only cookies with Secure and SameSite=Strict flags, 15-minute access tokens, 7-day refresh tokens

**Rationale**:
- HTTP-only cookies prevent XSS attacks (JavaScript cannot access tokens)
- Secure flag ensures tokens only sent over HTTPS
- SameSite=Strict prevents CSRF attacks
- Short-lived access tokens limit damage from token theft
- Refresh tokens enable seamless re-authentication

**Implementation Approach**:
- Better Auth issues JWT on login, stores in HTTP-only cookie
- Frontend automatically includes cookie in API requests
- Backend verifies JWT signature using shared secret
- Implement `/api/v1/auth/refresh` endpoint for token renewal
- Implement token blacklist or versioning for logout

**Best Practices**:
- Use strong secret (minimum 32 characters, cryptographically random)
- Include `exp` (expiration) and `iat` (issued at) claims
- Verify token signature, expiration, and required claims
- Use `HS256` algorithm for symmetric signing
- Rotate secrets periodically in production

**References**:
- JWT best practices: https://tools.ietf.org/html/rfc8725
- OWASP JWT security: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

---

### 6. User Data Isolation Strategy

**Decision**: Extract `user_id` from JWT token and filter all database queries by `user_id`

**Rationale**:
- Prevents users from accessing other users' data
- Enforces authorization at the database query level
- Eliminates need for `user_id` in URL paths (security risk)
- Simplifies API design (no need to validate URL user_id matches token user_id)

**Implementation Approach**:
- JWT middleware extracts `user_id` from token and attaches to request context
- All task queries include `WHERE user_id = {authenticated_user_id}`
- Service layer receives `user_id` from dependency injection
- Return 403 Forbidden if user attempts to access another user's resource

**Best Practices**:
- NEVER trust `user_id` from request body or URL parameters
- ALWAYS use `user_id` from verified JWT token
- Add database index on `user_id` column for performance
- Log unauthorized access attempts for security monitoring
- Use database-level row-level security (RLS) as additional layer

**References**:
- Multi-tenancy patterns: https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/tenancy-models
- PostgreSQL row-level security: https://www.postgresql.org/docs/current/ddl-rowsecurity.html

---

### 7. Frontend State Management

**Decision**: Use React Context API + useReducer for authentication state, local component state for task management

**Rationale**:
- Context API sufficient for simple global state (auth)
- Local state with React Query or SWR for server state (tasks)
- Avoids Redux complexity for MVP
- Can migrate to Zustand if state management needs grow

**Implementation Approach**:
- `AuthContext` provides: `user`, `isAuthenticated`, `login()`, `logout()`, `register()`
- Task components use local state + API calls
- Optimistic updates for better UX (update UI immediately, rollback on error)
- Use React Query or SWR for caching and automatic refetching

**Best Practices**:
- Keep authentication state separate from application state
- Use TypeScript for type-safe context
- Implement loading and error states
- Persist auth state to survive page refreshes (check token validity on mount)

**References**:
- React Context patterns: https://react.dev/learn/passing-data-deeply-with-context
- React Query: https://tanstack.com/query/latest

---

### 8. Testing Strategy

**Decision**: TDD with pytest (backend), Jest + React Testing Library (frontend), Playwright (E2E)

**Rationale**:
- TDD enforced by constitution (tests before implementation)
- pytest is standard for Python testing with excellent async support
- Jest + RTL is standard for React component testing
- Playwright provides reliable cross-browser E2E testing

**Implementation Approach**:
- **Backend Unit Tests**: Test services in isolation with mocked database
- **Backend Integration Tests**: Test API endpoints with test database
- **Frontend Component Tests**: Test components with mocked API
- **E2E Tests**: Test critical user flows (register, login, create task, mark complete)

**Coverage Requirements**:
- Minimum 70% code coverage for business logic
- 100% coverage for authentication and data persistence
- All bug fixes must include regression test

**Best Practices**:
- Use pytest fixtures for test data setup
- Use `pytest-asyncio` for async tests
- Use `TestClient` from FastAPI for integration tests
- Use `@testing-library/react` for component tests
- Use Playwright's auto-waiting for stable E2E tests

**References**:
- pytest documentation: https://docs.pytest.org/
- React Testing Library: https://testing-library.com/react
- Playwright: https://playwright.dev/

---

### 9. Environment Configuration

**Decision**: Use `.env` files with validation on startup, separate configs for dev/staging/prod

**Rationale**:
- Environment variables prevent hardcoding secrets
- Validation on startup fails fast if configuration is missing
- Separate configs enable environment-specific behavior

**Required Environment Variables**:

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<shared-secret-32-chars-minimum>
BETTER_AUTH_URL=http://localhost:3000
```

**Backend (.env)**:
```
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
BETTER_AUTH_SECRET=<shared-secret-32-chars-minimum>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
```

**Best Practices**:
- Provide `.env.example` files with dummy values
- Use Pydantic BaseSettings for type-safe configuration
- Validate required variables on application startup
- Never commit `.env` files to version control
- Use secret management services in production (AWS Secrets Manager, etc.)

**References**:
- Twelve-Factor App: https://12factor.net/config
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

---

### 10. Database Schema Design

**Decision**: Two tables (users, tasks) with foreign key constraint, indexes on user_id and completed

**Rationale**:
- Simple schema matches MVP requirements
- Foreign key ensures referential integrity
- Indexes optimize common queries (filter by user, filter by completed status)

**Schema**:

**users table**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**tasks table**:
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

**Best Practices**:
- Use Alembic for database migrations
- Add `updated_at` trigger to auto-update timestamp
- Use CASCADE on foreign key for automatic cleanup
- Consider soft delete (add `deleted_at` column) for data recovery

**References**:
- PostgreSQL best practices: https://wiki.postgresql.org/wiki/Don%27t_Do_This
- Alembic documentation: https://alembic.sqlalchemy.org/

---

## Summary

All technical decisions are documented with rationale and alternatives considered. Key decisions:

1. **Better Auth + JWT**: Stateless authentication with shared secret
2. **Next.js App Router**: Modern routing with route groups
3. **FastAPI + SQLModel**: Layered architecture with async support
4. **Neon PostgreSQL**: Serverless database with built-in pooling
5. **HTTP-only cookies**: Secure token storage preventing XSS
6. **User data isolation**: Extract user_id from JWT, filter all queries
7. **Context API**: Simple state management for MVP
8. **TDD with pytest/Jest**: Test-first development enforced
9. **Environment variables**: Configuration management with validation
10. **Simple schema**: Two tables with foreign key and indexes

All NEEDS CLARIFICATION items from Technical Context are now resolved. Ready to proceed to Phase 1: Design & Contracts.
