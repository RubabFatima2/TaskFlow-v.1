<!--
Sync Impact Report:
Version: 1.1.0 → 1.2.0
Bump Rationale: MINOR - Added technology stack mandate, Better Auth integration, Spec-Driven Development workflow, monorepo structure, aligned Task schema
Modified Principles:
  - VII. Authentication & Authorization → Enhanced with Better Auth + FastAPI integration details
  - Architecture Standards → Added Technology Stack and Monorepo Structure sections
  - Data Model → Aligned Task schema with HackathonII requirements (completed boolean instead of status)
Added Sections:
  - 0. Technology Stack (Mandatory)
  - XIV. Spec-Driven Development Workflow
  - Monorepo Structure (under Architecture Standards)
Removed Sections: None
Templates Requiring Updates:
  - ✅ .specify/templates/spec-template.md (reviewed - no changes needed)
  - ✅ .specify/templates/plan-template.md (reviewed - constitution check section already dynamic)
  - ✅ .specify/templates/tasks-template.md (reviewed - flexible task structure accommodates new principles)
Follow-up TODOs: None
-->

# TaskFlow2 Constitution - Todo Full Stack Web Application

## 0. Technology Stack (Mandatory)

**Rationale**: Standardizing the technology stack ensures consistency, leverages team expertise, and aligns with project requirements for a modern, scalable full-stack application.

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (strict mode enabled)
- **Styling**: Tailwind CSS
- **State Management**: Context API + useReducer or Zustand
- **HTTP Client**: Fetch API or Axios

### Backend
- **Framework**: Python FastAPI
- **ORM**: SQLModel
- **Validation**: Pydantic (built into FastAPI)
- **Authentication**: Better Auth (frontend) + JWT verification (backend)

### Database
- **Provider**: Neon Serverless PostgreSQL
- **Migrations**: Alembic or SQLModel migrations
- **Connection Pooling**: Built-in Neon pooling

### Authentication
- **Frontend**: Better Auth (JavaScript/TypeScript library)
- **Backend**: JWT token verification with shared secret
- **Token Format**: JSON Web Tokens (JWT)
- **Shared Secret**: `BETTER_AUTH_SECRET` environment variable (MUST be identical in frontend and backend)

### Development Tools
- **Spec-Driven Development**: Claude Code + Spec-Kit Plus (mandatory workflow)
- **Containerization**: Docker + docker-compose for local development
- **Version Control**: Git with feature branches

### Monorepo Structure
```
TaskFlow2/
├── .specify/                    # Spec-Kit Plus configuration
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   └── scripts/
├── specs/                       # Feature specifications
│   ├── 001-fullstack-todo-app/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   └── tasks.md
├── frontend/                    # Next.js application
│   ├── CLAUDE.md               # Frontend-specific instructions
│   ├── app/                    # Next.js App Router
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── .env.local
├── backend/                     # FastAPI application
│   ├── CLAUDE.md               # Backend-specific instructions
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── middleware/
│   ├── tests/
│   ├── requirements.txt
│   └── .env
├── docker-compose.yml
├── CLAUDE.md                    # Root project instructions
├── AGENTS.md                    # Agent configuration
└── README.md
```

## Core Principles

### I. User-Centric Design
- Prioritize user experience and intuitive interfaces
- Minimize friction in task creation, editing, and completion
- Provide immediate visual feedback for all user actions
- Support keyboard shortcuts for power users
- Never lose user data; implement auto-save and conflict resolution

### II. Test-First Development (NON-NEGOTIABLE)
- TDD mandatory: Tests written → User approved → Tests fail → Then implement
- Red-Green-Refactor cycle strictly enforced
- Minimum 70% code coverage for business logic
- 100% coverage for critical paths (authentication, data persistence)
- All bug fixes must include a regression test

### III. Security by Default
- Implement secure password hashing (bcrypt, Argon2)
- Validate all user inputs on both client and server
- Use parameterized queries to prevent SQL injection
- Never log sensitive data (passwords, tokens, PII)
- Use HTTPS for all communications
- Store secrets in environment variables, never in code

### IV. API-First Architecture
- RESTful conventions: proper HTTP verbs (GET, POST, PUT, DELETE)
- Consistent URL structure: `/api/v1/resource` (versioned)
- **User ID from JWT**: NEVER include `user_id` in URL path; extract from JWT token
  - ✅ Correct: `GET /api/v1/tasks` (user_id from token)
  - ❌ Wrong: `GET /api/v1/users/{user_id}/tasks` (redundant, security risk)
- Standard HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- JSON request/response format with clear schemas
- Stateless API design for horizontal scaling

### V. Simplicity and Maintainability
- Start with minimal viable features; add complexity only when justified
- Self-documenting code with clear variable and function names
- Functions should do one thing and do it well (Single Responsibility)
- Maximum function length: 50 lines (guideline)
- Avoid premature optimization; measure before optimizing

### VI. Data Integrity
- Maintain data consistency between client and server
- Implement soft delete (archive) rather than hard delete for tasks
- Enforce foreign key constraints in database
- Provide clear error messages when operations fail
- Auto-save task changes after 2 seconds of inactivity

### VII. Authentication & Authorization (Better Auth + FastAPI Integration)
**Rationale**: Secure user authentication and data isolation are critical for multi-user applications. Better Auth (frontend) + JWT verification (backend) provides stateless, scalable auth while enforcing strict user-level data boundaries.

#### Better Auth Configuration (Frontend - Next.js)
- **Library**: Better Auth (JavaScript/TypeScript authentication library)
- **JWT Plugin**: MUST enable JWT plugin to issue tokens on login
- **Shared Secret**: Use `BETTER_AUTH_SECRET` environment variable (MUST match backend)
- **Token Issuance**: Better Auth creates session and issues JWT token on successful login
- **Token Storage**: Store JWT in HTTP-only cookies with `Secure` and `SameSite=Strict` flags
- **Token Attachment**: Frontend MUST attach JWT token to every API request in `Authorization: Bearer <token>` header

#### FastAPI JWT Verification (Backend - Python)
- **JWT Library**: Use `python-jose[cryptography]` or `PyJWT` for token verification
- **Shared Secret**: Use same `BETTER_AUTH_SECRET` environment variable as frontend
- **Middleware**: Implement JWT verification middleware to extract and validate tokens
- **Token Structure**: Tokens MUST include `user_id`, `email`, `exp` (expiration), and `iat` (issued at) claims
- **User Extraction**: Decode JWT to extract `user_id` and attach to request context
- **Authentication Requirement**: All API endpoints MUST require authentication unless explicitly marked as public (e.g., `/api/v1/health`, OPTIONS requests)
- **User-Level Data Isolation**: Users MUST only access their own tasks; enforce `user_id` filtering in all database queries
  - Example: `SELECT * FROM tasks WHERE user_id = {authenticated_user_id}`
  - NEVER trust `user_id` from request body/URL; ALWAYS use `user_id` from JWT token

#### Token Expiration Strategy
- Access tokens: 15-minute expiration (configurable via Better Auth)
- Refresh tokens: 7-day expiration
- Implement token refresh endpoint (`/api/v1/auth/refresh`)

#### API Endpoint Security
- **Protected Endpoints**: All `/api/v1/tasks/*` endpoints require valid JWT
- **Public Endpoints**: `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/health`
- **401 Unauthorized**: Return when token is missing, invalid, or expired
- **403 Forbidden**: Return when user attempts to access another user's resources
- **Token Validation**: Verify signature, expiration, and required claims on every request

#### Security Benefits
- **User Isolation**: Each user only sees their own tasks
- **Stateless Auth**: Backend doesn't need to call frontend to verify users
- **Token Expiry**: JWTs expire automatically (e.g., after 15 minutes)
- **No Shared DB Session**: Frontend and backend verify auth independently
- **Revocation**: Implement token blacklist or versioning for logout and security events

### VIII. State Management Strategy (Frontend)
**Rationale**: Consistent state management prevents bugs, improves maintainability, and ensures predictable UI behavior across the application.

- **Single Source of Truth**: Application state MUST have one authoritative source
- **State Management Library**: Use established patterns (Redux, Zustand, Context API + useReducer)
- **State Structure**:
  - Authentication state (user, tokens, auth status)
  - Task state (tasks list, filters, selected task)
  - UI state (modals, loading states, errors)
- **State Synchronization**: Keep client state in sync with server via optimistic updates + rollback on failure
- **Immutable Updates**: Never mutate state directly; use immutable update patterns
- **Derived State**: Compute derived values (filtered tasks, counts) from base state rather than storing separately
- **Persistence**: Persist critical state (auth tokens) to survive page refreshes
- **State Hydration**: Load initial state from server on app mount

### IX. API Contract & Schema Enforcement
**Rationale**: Explicit API contracts prevent integration bugs, enable independent frontend/backend development, and serve as living documentation.

- **Schema Definition**: Define request/response schemas using JSON Schema, OpenAPI, or TypeScript types
- **Request Validation**: Validate all incoming requests against schemas; reject invalid requests with 400 Bad Request
- **Response Validation**: Ensure all responses match documented schemas (enforce in tests)
- **Versioning**: Use URL versioning (`/api/v1/`, `/api/v2/`) for breaking changes
- **Contract Testing**: Implement contract tests to verify API adherence to schemas
- **Documentation**: Auto-generate API documentation from schemas (Swagger/OpenAPI)
- **Type Safety**: Share types between frontend and backend where possible (TypeScript monorepo, code generation)
- **Breaking Changes**: Never introduce breaking changes within a version; increment version for incompatible changes

### X. Environment & Configuration Management
**Rationale**: Proper configuration management prevents security leaks, enables environment-specific behavior, and simplifies deployment across dev/staging/production.

- **Environment Variables**: Store all configuration in environment variables (`.env` files)
- **Required Variables**: Document all required environment variables in `.env.example`
- **Secret Management**: 
  - Never commit secrets to version control
  - Use `.gitignore` to exclude `.env` files
  - Use secret management services in production (AWS Secrets Manager, HashiCorp Vault)
- **Environment-Specific Config**:
  - Development: `.env.development` (verbose logging, debug mode)
  - Staging: `.env.staging` (production-like, test data)
  - Production: `.env.production` (minimal logging, optimized)
- **Configuration Validation**: Validate required environment variables on application startup; fail fast if missing
- **Default Values**: Provide sensible defaults for non-sensitive configuration
- **Configuration Access**: Centralize configuration access through a config module/service
- **No Hardcoded Values**: Database URLs, API keys, feature flags MUST come from environment variables

### XI. Accessibility Standards
**Rationale**: Accessible applications serve all users, including those with disabilities, and often improve usability for everyone.

- **WCAG 2.1 Level AA Compliance**: Target WCAG 2.1 Level AA as minimum standard
- **Semantic HTML**: Use proper HTML elements (`<button>`, `<nav>`, `<main>`, `<article>`)
- **Keyboard Navigation**: All interactive elements MUST be keyboard accessible (Tab, Enter, Escape)
- **Focus Management**: Visible focus indicators; manage focus for modals and dynamic content
- **ARIA Labels**: Use ARIA attributes where semantic HTML insufficient (`aria-label`, `aria-describedby`, `role`)
- **Color Contrast**: Minimum 4.5:1 contrast ratio for normal text, 3:1 for large text
- **Screen Reader Support**: Test with screen readers (NVDA, JAWS, VoiceOver)
- **Form Accessibility**: 
  - Associate labels with inputs (`<label for="...">`)
  - Provide error messages with `aria-invalid` and `aria-describedby`
  - Group related inputs with `<fieldset>` and `<legend>`
- **Alternative Text**: Provide meaningful alt text for images; use `alt=""` for decorative images
- **Responsive Design**: Support zoom up to 200% without loss of functionality

### XII. Error Handling & User Experience
**Rationale**: Clear, actionable error messages reduce user frustration, improve support efficiency, and build trust.

- **User-Friendly Messages**: Display human-readable error messages, not technical jargon or stack traces
- **Actionable Guidance**: Tell users what went wrong AND how to fix it
  - Bad: "Error 500"
  - Good: "Unable to save task. Please check your connection and try again."
- **Error Categories**:
  - Validation errors: Highlight specific fields with inline messages
  - Network errors: "Connection lost. Retrying..."
  - Authorization errors: "Session expired. Please log in again."
  - Server errors: "Something went wrong. Our team has been notified."
- **Error Logging**: Log all errors server-side with context (user_id, endpoint, timestamp, stack trace)
- **Error Tracking**: Integrate error tracking service (Sentry, Rollbar) for production monitoring
- **Graceful Degradation**: Application MUST remain functional when non-critical features fail
- **Retry Logic**: Implement exponential backoff for transient failures (network, rate limits)
- **Error Recovery**: Provide clear recovery paths (retry button, refresh, contact support)
- **Toast/Notification System**: Use consistent notification system for success, warning, error messages
- **Form Validation**: Show validation errors inline, near the relevant field, as user types or on blur

### XIII. Rate Limiting & Abuse Prevention
**Rationale**: Rate limiting protects against abuse, ensures fair resource allocation, and maintains service availability for all users.

- **Endpoint-Specific Limits**:
  - Authentication endpoints: 5 requests per minute per IP (prevent brute force)
  - Read endpoints: 100 requests per minute per user
  - Write endpoints: 30 requests per minute per user
  - Public endpoints: 20 requests per minute per IP
- **Rate Limit Headers**: Return standard headers in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining in window
  - `X-RateLimit-Reset`: Timestamp when limit resets
- **Rate Limit Response**: Return 429 Too Many Requests with `Retry-After` header
- **Rate Limit Strategy**: Use sliding window or token bucket algorithm
- **User Feedback**: Display rate limit information in UI when approaching limits
- **Bypass for Trusted Clients**: Allow rate limit bypass for internal services (API keys, IP whitelist)
- **DDoS Protection**: Implement additional protections at infrastructure level (CloudFlare, AWS WAF)
- **Monitoring**: Alert on unusual rate limit patterns (potential attacks or bugs)

### XIV. Spec-Driven Development Workflow (Mandatory)
**Rationale**: Spec-Driven Development ensures clear requirements, prevents scope creep, enables AI-assisted development, and maintains traceability from requirements to implementation.

#### Workflow Phases (Strictly Enforced)
1. **Specification Phase**: Write detailed feature specification (`spec.md`)
   - Define user stories, acceptance criteria, and constraints
   - Document API contracts, data models, and UI requirements
   - Get user approval before proceeding

2. **Planning Phase**: Generate implementation plan (`plan.md`)
   - Break specification into architectural decisions
   - Identify dependencies, risks, and technical approach
   - Create ADRs for significant decisions
   - Get user approval before proceeding

3. **Task Generation Phase**: Break plan into actionable tasks (`tasks.md`)
   - Each task MUST be testable and have clear acceptance criteria
   - Tasks MUST be ordered by dependencies
   - Each task includes test cases (Red-Green-Refactor)
   - Get user approval before proceeding

4. **Implementation Phase**: Let Claude Code generate the code
   - **NO MANUAL CODING ALLOWED** - All code generated via Claude Code
   - Follow TDD: Write tests → Tests fail (Red) → Implement → Tests pass (Green) → Refactor
   - Each task completed sequentially with user verification

#### Tools and Artifacts
- **Claude Code**: AI-powered development assistant (mandatory)
- **Spec-Kit Plus**: Specification and planning framework
- **Artifacts**: `spec.md`, `plan.md`, `tasks.md`, ADRs, PHRs (Prompt History Records)
- **Version Control**: All artifacts committed to `specs/<feature-name>/` directory

#### Compliance Requirements
- All features MUST follow this workflow (no exceptions)
- Each phase MUST be approved by user before proceeding to next phase
- All code changes MUST be traceable to a task in `tasks.md`
- All tasks MUST be traceable to a requirement in `spec.md`
- Deviations from spec MUST be documented in ADR and spec updated

#### Benefits
- Clear requirements reduce ambiguity and rework
- AI-assisted development accelerates implementation
- Traceability from requirements to code
- Consistent quality and documentation
- Easier onboarding and knowledge transfer

## Performance Standards

### Response Time Targets
- API endpoints: < 200ms for simple queries, < 1s for complex operations
- Page load time: < 2s for initial load, < 500ms for subsequent navigation
- Database queries: < 100ms for indexed queries
- UI interactions: < 100ms perceived response time

### Optimization Requirements
- Implement database indexing on frequently queried fields (user_id, completed, created_at)
- Use pagination for large data sets (default: 20-50 items per page)
- Lazy load non-critical resources
- Minimize bundle size (code splitting, tree shaking)

## Code Quality Standards

### Consistency
- Follow language-specific style guides (PEP 8 for Python, Airbnb for JavaScript)
- Use linters and formatters (ESLint, Prettier, Black, etc.)
- Consistent naming conventions across the codebase
- Consistent error handling patterns

### Error Handling
- Never swallow errors silently
- Log errors with sufficient context for debugging
- Return meaningful error messages to users
- Validate inputs at system boundaries

### Dependencies
- Minimize external dependencies
- Keep dependencies up to date
- Avoid dependencies with known security vulnerabilities
- Use lock files (package-lock.json, Pipfile.lock, etc.)

## Architecture Standards

### Layering
- **Presentation Layer:** UI components, state management, routing
- **API Layer:** HTTP endpoints, request/response handling, validation
- **Business Logic Layer:** Domain models, use cases, business rules
- **Data Access Layer:** Repository pattern, database queries, migrations

### Data Model (Core Entities)
- **User:** id, email, password_hash, created_at, updated_at
- **Task:** id, user_id, title (1-200 characters, required), description (optional), completed (boolean, default: false), created_at, updated_at
- Enforce foreign key constraints (task.user_id → user.id)
- Add indexes on user_id, completed, created_at

## Testing Standards

### Test Types Required
- **Unit Tests:** Test individual functions/methods in isolation
- **Integration Tests:** Test API endpoints and database interactions
- **E2E Tests:** Test critical user flows (login, create task, complete task)
- **Component Tests:** Test UI components with mock data

### Test Quality
- Tests should be fast (unit tests < 100ms, integration tests < 1s)
- Tests should be deterministic (no flaky tests)
- Tests should be independent (no shared state)
- Use descriptive test names: `test_user_cannot_delete_others_tasks`
- Follow AAA pattern: Arrange, Act, Assert

## Development Workflow

### Version Control
- Use Git with feature branches
- Branch naming: `feature/task-description`, `bugfix/issue-description`
- Commit messages: Clear, concise, imperative mood
- Never commit secrets or sensitive data

### Code Review
- All code must be reviewed before merging
- Reviewers check for: correctness, tests, security, performance
- Address all review comments before merge

### CI/CD
- Run tests automatically on every commit
- Run linters and formatters in CI pipeline
- Block merges if tests fail
- Implement rollback strategy

## Definition of Done

A feature is considered "done" when:
- [ ] Code is written and follows all standards in this constitution
- [ ] Unit tests are written and passing (>70% coverage)
- [ ] Integration tests are written for API endpoints
- [ ] Code has been reviewed and approved
- [ ] Documentation is updated
- [ ] Feature works in staging environment
- [ ] No known security vulnerabilities
- [ ] Performance meets defined standards
- [ ] Authentication/authorization requirements verified (if applicable)
- [ ] API contracts validated and documented
- [ ] Accessibility standards met (WCAG 2.1 AA)
- [ ] Error handling and user feedback implemented
- [ ] Rate limiting configured (if applicable)

## Governance

- This constitution supersedes all other practices
- All PRs/reviews must verify compliance with these principles
- Amendments require documentation in ADR and team approval
- Technical debt must be documented with TODO/FIXME comments
- Allocate time to address technical debt regularly

**Version**: 1.2.0 | **Ratified**: 2026-04-10 | **Last Amended**: 2026-04-10
