# Quickstart Guide: Full-Stack Todo Web Application

**Feature**: 001-fullstack-todo-app  
**Date**: 2026-04-10  
**Status**: Ready for Implementation

## Overview

This guide provides step-by-step instructions for setting up and running the full-stack todo application locally. The application consists of a Next.js 16+ frontend and FastAPI backend with Neon Serverless PostgreSQL.

## Prerequisites

- **Node.js**: 18.x or higher
- **Python**: 3.11 or higher
- **Git**: Latest version
- **Neon Account**: Free tier account at https://neon.tech
- **Code Editor**: VS Code recommended

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Next.js 16+   │────────▶│   FastAPI       │────────▶│  Neon PostgreSQL│
│   (Frontend)    │  HTTP   │   (Backend)     │  SQL    │   (Database)    │
│   Port 3000     │◀────────│   Port 8000     │◀────────│   Cloud Hosted  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
      │                              │
      │                              │
      ▼                              ▼
Better Auth (JWT)          JWT Verification
HTTP-only cookies          Shared Secret
```

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd TaskFlow2
git checkout 001-fullstack-todo-app
```

## Step 2: Setup Neon PostgreSQL Database

### 2.1 Create Neon Project

1. Go to https://neon.tech and sign up/login
2. Click "Create Project"
3. Choose a project name: `todo-app-dev`
4. Select region closest to you
5. Click "Create Project"

### 2.2 Get Connection String

1. In Neon dashboard, click "Connection Details"
2. Copy the connection string (it looks like):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
3. Save this for the next step

## Step 3: Setup Backend (FastAPI)

### 3.1 Navigate to Backend Directory

```bash
cd backend
```

### 3.2 Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.4 Create Environment File

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# JWT Configuration
BETTER_AUTH_SECRET=your-super-secret-key-minimum-32-characters-long-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**IMPORTANT**: 
- Replace `DATABASE_URL` with your Neon connection string from Step 2.2
- Change `BETTER_AUTH_SECRET` to a random 32+ character string
- Keep this file secret (already in .gitignore)

### 3.5 Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Create users and tasks tables"

# Apply migrations
alembic upgrade head
```

### 3.6 Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should now be running at: http://localhost:8000

**Verify**:
- Open http://localhost:8000/docs (Swagger UI)
- Open http://localhost:8000/api/v1/health (should return `{"status": "healthy"}`)

## Step 4: Setup Frontend (Next.js)

### 4.1 Open New Terminal

Keep backend running, open a new terminal window.

### 4.2 Navigate to Frontend Directory

```bash
cd frontend
```

### 4.3 Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 4.4 Create Environment File

Create `frontend/.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key-minimum-32-characters-long-change-this
BETTER_AUTH_URL=http://localhost:3000
```

**IMPORTANT**: 
- Use the SAME `BETTER_AUTH_SECRET` as backend/.env
- This shared secret is critical for JWT verification

### 4.5 Start Frontend Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Frontend should now be running at: http://localhost:3000

## Step 5: Verify Installation

### 5.1 Check Backend Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-04-10T13:44:17.844Z"
}
```

### 5.2 Check Frontend

1. Open http://localhost:3000 in browser
2. You should see the landing page
3. No console errors in browser DevTools

### 5.3 Test Registration Flow

1. Navigate to http://localhost:3000/register
2. Enter email: `test@example.com`
3. Enter password: `TestPass123`
4. Click "Register"
5. Should redirect to login page

### 5.4 Test Login Flow

1. Navigate to http://localhost:3000/login
2. Enter email: `test@example.com`
3. Enter password: `TestPass123`
4. Click "Login"
5. Should redirect to tasks page

### 5.5 Test Task Creation

1. On tasks page, click "New Task"
2. Enter title: "My first task"
3. Enter description: "Testing the app"
4. Click "Create"
5. Task should appear in the list

## Step 6: Run Tests

### 6.1 Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth_service.py

# Run integration tests only
pytest tests/integration/
```

### 6.2 Frontend Tests

```bash
cd frontend

# Run unit and component tests
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests (requires backend running)
npm run test:e2e
```

## Development Workflow

### Hot Reload

Both frontend and backend support hot reload:
- **Backend**: Changes to Python files automatically reload the server
- **Frontend**: Changes to TypeScript/React files automatically refresh the browser

### Database Changes

When modifying models:

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Common Issues & Solutions

### Issue: Backend won't start - "ModuleNotFoundError"

**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution**: Verify Neon connection string
```bash
# Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('your-connection-string'); print('Connected!')"
```

### Issue: Frontend can't connect to backend

**Solution**: Check CORS configuration
- Verify `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`
- Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local` is `http://localhost:8000`

### Issue: JWT authentication fails

**Solution**: Verify shared secret matches
- Check `BETTER_AUTH_SECRET` is IDENTICAL in both `backend/.env` and `frontend/.env.local`
- Secret must be minimum 32 characters

### Issue: "Port already in use"

**Solution**: Kill existing process or use different port
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn app.main:app --reload --port 8001
```

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | Neon PostgreSQL connection string |
| BETTER_AUTH_SECRET | Yes | - | Shared secret for JWT (32+ chars) |
| JWT_ALGORITHM | No | HS256 | JWT signing algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 15 | Access token expiration |
| REFRESH_TOKEN_EXPIRE_DAYS | No | 7 | Refresh token expiration |
| CORS_ORIGINS | Yes | - | Allowed frontend origins |
| ENVIRONMENT | No | development | Environment name |

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NEXT_PUBLIC_API_URL | Yes | - | Backend API URL |
| BETTER_AUTH_SECRET | Yes | - | Shared secret for JWT (must match backend) |
| BETTER_AUTH_URL | Yes | - | Frontend URL for Better Auth |

## Next Steps

1. **Read the Spec**: Review `specs/001-fullstack-todo-app/spec.md` for requirements
2. **Review Data Model**: Check `specs/001-fullstack-todo-app/data-model.md` for schema
3. **Explore API Contracts**: See `specs/001-fullstack-todo-app/contracts/openapi.yaml`
4. **Start Implementation**: Follow tasks in `specs/001-fullstack-todo-app/tasks.md` (generated by `/sp.tasks`)

## Useful Commands

### Backend

```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Create migration
alembic revision --autogenerate -m "message"

# Apply migrations
alembic upgrade head

# Format code
black app/

# Lint code
flake8 app/
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Support

- **Documentation**: See `specs/001-fullstack-todo-app/` directory
- **API Docs**: http://localhost:8000/docs
- **Constitution**: `.specify/memory/constitution.md`

## Security Checklist

Before deploying to production:

- [ ] Change `BETTER_AUTH_SECRET` to a strong random value
- [ ] Use HTTPS for all connections
- [ ] Enable Neon connection pooling
- [ ] Set `ENVIRONMENT=production` in backend
- [ ] Update `CORS_ORIGINS` to production frontend URL
- [ ] Enable rate limiting
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure database backups
- [ ] Review and test all authentication flows
- [ ] Run security audit: `npm audit` and `pip-audit`

---

**Last Updated**: 2026-04-10  
**Version**: 1.0.0
