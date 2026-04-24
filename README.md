# TaskFlow2

<div align="center">

**A modern, secure, full-stack todo application built with Next.js and FastAPI**

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=flat&logo=postgresql)](https://neon.tech/)

</div>

---

## Overview

TaskFlow2 is a production-ready todo application that demonstrates modern full-stack development practices. Built with **Spec-Driven Development (SDD)**, it features robust authentication, real-time updates, and enterprise-grade security patterns.

### Key Highlights

- **🔐 Secure Authentication** - JWT-based auth with HTTP-only cookies, bcrypt password hashing, and Better Auth integration
- **🎯 User Isolation** - Complete data separation ensuring users only access their own tasks
- **⚡ Real-time Updates** - Optimistic UI updates with automatic rollback on failure
- **🧪 Test-Driven** - Comprehensive test coverage with unit, integration, and E2E tests
- **📱 Responsive Design** - Mobile-first UI built with Tailwind CSS
- **🚀 Production Ready** - Environment-based configuration, error tracking, and rate limiting
- **📋 Spec-Driven** - Complete traceability from requirements to implementation

---

## Features

### Core Functionality

- ✅ **User Management**
  - Secure registration with email validation
  - JWT-based authentication with refresh tokens
  - Session management with automatic token refresh
  - Secure logout with token revocation

- ✅ **Task Management**
  - Create tasks with title and description
  - Mark tasks as complete/incomplete
  - Edit task details
  - Delete tasks
  - Real-time status updates

- ✅ **Security**
  - Bcrypt password hashing
  - HTTP-only cookies with Secure and SameSite flags
  - CORS protection
  - Input validation with Pydantic
  - SQL injection prevention
  - Rate limiting on authentication endpoints

- ✅ **User Experience**
  - Optimistic UI updates
  - Loading states and error handling
  - Keyboard shortcuts
  - Accessible design (WCAG 2.1 AA)
  - Responsive layout

---

## Tech Stack

### Frontend
- **Framework**: [Next.js 14+](https://nextjs.org/) with App Router
- **Language**: [TypeScript](https://www.typescriptlang.org/) (strict mode)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Authentication**: [Better Auth](https://www.better-auth.com/)
- **State Management**: React Context API + useReducer
- **Testing**: Jest, React Testing Library, Playwright

### Backend
- **Framework**: [FastAPI 0.110+](https://fastapi.tiangolo.com/)
- **Language**: Python 3.11+
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/)
- **Validation**: Pydantic
- **Authentication**: JWT with python-jose
- **Database**: [Neon Serverless PostgreSQL](https://neon.tech/)
- **Migrations**: Alembic
- **Testing**: Pytest, pytest-asyncio

### DevOps
- **Containerization**: Docker + Docker Compose
- **Version Control**: Git with feature branches
- **Development**: Spec-Driven Development (SDD) with Claude Code

---

## Project Structure

```
TaskFlow2/
├── .specify/                    # Spec-Kit Plus configuration
│   ├── memory/
│   │   └── constitution.md     # Project principles and standards
│   ├── templates/              # Spec, plan, and task templates
│   └── scripts/                # Automation scripts
│
├── specs/                       # Feature specifications
│   └── 001-fullstack-todo-app/
│       ├── spec.md             # Requirements and user stories
│       ├── plan.md             # Architecture and design
│       └── tasks.md            # Implementation tasks
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── models/            # SQLModel database models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── routes/            # API endpoint handlers
│   │   ├── services/          # Business logic layer
│   │   ├── middleware/        # JWT authentication middleware
│   │   ├── utils/             # Utilities (security, dependencies)
│   │   ├── config.py          # Configuration management
│   │   └── database.py        # Database connection
│   ├── tests/                 # Backend tests
│   ├── alembic/               # Database migrations
│   ├── requirements.txt       # Python dependencies
│   ├── pytest.ini             # Pytest configuration
│   └── CLAUDE.md              # Backend-specific instructions
│
├── frontend/                   # Next.js application
│   ├── app/                   # Next.js App Router
│   │   ├── (auth)/           # Authentication pages
│   │   └── (dashboard)/      # Protected dashboard pages
│   ├── components/            # React components
│   │   ├── auth/             # Authentication components
│   │   ├── tasks/            # Task management components
│   │   └── ui/               # Reusable UI components
│   ├── lib/                  # Utilities and API client
│   ├── hooks/                # Custom React hooks
│   ├── context/              # React Context providers
│   ├── tests/                # Frontend tests
│   ├── package.json          # Node dependencies
│   └── CLAUDE.md             # Frontend-specific instructions
│
├── history/                    # Development history
│   ├── prompts/               # Prompt History Records (PHRs)
│   └── adr/                   # Architecture Decision Records
│
├── docker-compose.yml         # Local development setup
├── CLAUDE.md                  # Root project instructions
├── AGENTS.md                  # AI agent configuration
└── README.md                  # This file
```

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.11+
- **PostgreSQL** (Neon account or local instance)
- **Git**

### Quick Start

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd TaskFlow2
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration
# Required variables:
#   DATABASE_URL=postgresql://user:password@host:5432/taskflow
#   BETTER_AUTH_SECRET=your-secret-key-min-32-chars
#   JWT_ALGORITHM=HS256
#   ACCESS_TOKEN_EXPIRE_MINUTES=15
#   REFRESH_TOKEN_EXPIRE_DAYS=7
#   CORS_ORIGINS=http://localhost:3000

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local with your configuration
# Required variables:
#   NEXT_PUBLIC_API_URL=http://localhost:8000
#   BETTER_AUTH_SECRET=your-secret-key-min-32-chars  # MUST match backend!
#   BETTER_AUTH_URL=http://localhost:3000

# Start the development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

#### 4. Verify Setup

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Create your first task
4. Mark it as complete

---

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login user | No |
| POST | `/api/v1/auth/logout` | Logout user | Yes |
| POST | `/api/v1/auth/refresh` | Refresh access token | Yes (refresh token) |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/tasks` | Get all user tasks | Yes |
| POST | `/api/v1/tasks` | Create new task | Yes |
| GET | `/api/v1/tasks/{task_id}` | Get specific task | Yes |
| PUT | `/api/v1/tasks/{task_id}` | Update task | Yes |
| DELETE | `/api/v1/tasks/{task_id}` | Delete task | Yes |

### Request/Response Examples

#### Register User

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-04-24T16:00:00Z"
}
```

#### Create Task

```bash
POST /api/v1/tasks
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive README and API docs"
}

# Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive README and API docs",
  "completed": false,
  "created_at": "2026-04-24T16:00:00Z",
  "updated_at": "2026-04-24T16:00:00Z"
}
```

---

## Development

### Running Tests

#### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

#### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e
```

### Code Quality

#### Backend

```bash
# Format code with Black
black app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

#### Frontend

```bash
# Lint with ESLint
npm run lint

# Format with Prettier
npm run format

# Type checking
npm run type-check
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Deployment

### Environment Variables

#### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/taskflow

# Authentication
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://yourdomain.com

# Environment
ENVIRONMENT=production
```

#### Frontend (.env.local)

```env
# API
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Authentication
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-change-in-production
BETTER_AUTH_URL=https://yourdomain.com
```

### Production Checklist

- [ ] Set strong `BETTER_AUTH_SECRET` (min 32 characters)
- [ ] Use HTTPS for all communications
- [ ] Configure CORS for production domain only
- [ ] Set up database backups
- [ ] Enable error tracking (Sentry, Rollbar)
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Review and update security headers
- [ ] Enable database connection pooling
- [ ] Configure CDN for static assets
- [ ] Set up CI/CD pipeline
- [ ] Review and test rollback procedures

---

## Architecture

### Authentication Flow

```
┌─────────┐                 ┌──────────┐                 ┌─────────┐
│ Browser │                 │ Next.js  │                 │ FastAPI │
└────┬────┘                 └────┬─────┘                 └────┬────┘
     │                           │                            │
     │  1. Login Request         │                            │
     ├──────────────────────────>│                            │
     │                           │  2. Forward Credentials    │
     │                           ├───────────────────────────>│
     │                           │                            │
     │                           │  3. Verify & Issue JWT     │
     │                           │<───────────────────────────┤
     │  4. Set HTTP-only Cookie  │                            │
     │<──────────────────────────┤                            │
     │                           │                            │
     │  5. API Request + Cookie  │                            │
     ├──────────────────────────>│                            │
     │                           │  6. Forward with JWT       │
     │                           ├───────────────────────────>│
     │                           │                            │
     │                           │  7. Verify JWT & Respond   │
     │                           │<───────────────────────────┤
     │  8. Return Data           │                            │
     │<──────────────────────────┤                            │
```

### Data Isolation

All database queries automatically filter by `user_id` extracted from JWT token:

```python
# ✅ Correct - user_id from JWT token
@router.get("/tasks")
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = await Task.get_by_user_id(current_user.id)
    return tasks

# ❌ Wrong - user_id from URL (security risk)
@router.get("/users/{user_id}/tasks")
async def get_tasks(user_id: int):
    tasks = await Task.get_by_user_id(user_id)  # Any user can access any tasks!
    return tasks
```

---

## Spec-Driven Development

This project follows **Spec-Driven Development (SDD)**, ensuring every line of code traces back to a documented requirement.

### Workflow

1. **Specify** (`spec.md`) - Define requirements, user stories, and acceptance criteria
2. **Plan** (`plan.md`) - Design architecture and technical approach
3. **Tasks** (`tasks.md`) - Break down into testable implementation tasks
4. **Implement** - Write code following Test-Driven Development (TDD)

### Benefits

- Clear requirements reduce ambiguity
- AI-assisted development with Claude Code
- Complete traceability from requirements to code
- Consistent quality and documentation
- Easier onboarding and knowledge transfer

### Documentation

- **Specifications**: `specs/001-fullstack-todo-app/`
- **Architecture Decisions**: `history/adr/`
- **Development History**: `history/prompts/`
- **Project Principles**: `.specify/memory/constitution.md`

---

## Security

### Authentication

- Passwords hashed with bcrypt (cost factor: 12)
- JWT tokens with 15-minute expiration
- Refresh tokens with 7-day expiration
- HTTP-only cookies with Secure and SameSite=Strict flags
- Token revocation on logout

### Authorization

- User-level data isolation enforced at database query level
- JWT token validation on every protected endpoint
- 401 Unauthorized for missing/invalid tokens
- 403 Forbidden for unauthorized resource access

### Input Validation

- All inputs validated with Pydantic schemas
- SQL injection prevention with parameterized queries
- XSS prevention with proper output encoding
- CSRF protection with SameSite cookies

### Rate Limiting

- Authentication endpoints: 5 requests/minute per IP
- Read endpoints: 100 requests/minute per user
- Write endpoints: 30 requests/minute per user

---

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Follow Spec-Driven Development workflow
3. Write tests first (TDD)
4. Implement feature
5. Ensure all tests pass
6. Submit pull request

### Code Standards

- Follow `.specify/memory/constitution.md` principles
- Maintain test coverage >70%
- Use conventional commit messages
- Update documentation for new features

---

## Troubleshooting

### Common Issues

#### JWT Token Mismatch

**Problem**: 401 Unauthorized errors after login

**Solution**: Ensure `BETTER_AUTH_SECRET` is identical in frontend and backend `.env` files

#### Database Connection Failed

**Problem**: Cannot connect to PostgreSQL

**Solution**: 
- Verify `DATABASE_URL` in backend `.env`
- Check Neon database is running
- Ensure IP is whitelisted in Neon dashboard

#### CORS Errors

**Problem**: Browser blocks API requests

**Solution**: Add frontend URL to `CORS_ORIGINS` in backend `.env`

#### Port Already in Use

**Problem**: Cannot start server

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Acknowledgments

- Built with [Claude Code](https://claude.ai/code) - AI-powered development assistant
- Spec-Driven Development methodology
- Better Auth for authentication
- Neon for serverless PostgreSQL

---

## Support

- **Documentation**: See `specs/` directory for detailed specifications
- **Issues**: Report bugs via GitHub Issues
- **Questions**: Check existing issues or create a new one

---

<div align="center">

**Built with professioanlism using Spec-Driven Development**

[Documentation](./specs/001-fullstack-todo-app/) • [API Docs](http://localhost:8000/docs) • [Report Bug](https://github.com/yourusername/taskflow2/issues)

</div>
