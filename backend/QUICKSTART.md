# Backend Quick Start Guide

## Prerequisites
- Python 3.11+
- PostgreSQL database (Neon recommended)
- Git

## Setup Steps

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy example file
cp .env.example .env

# Edit .env with your settings
# REQUIRED: Update DATABASE_URL with your Neon PostgreSQL connection string
# REQUIRED: Update BETTER_AUTH_SECRET with a secure random string (32+ chars)
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify Installation

### Check Health Endpoint
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development"
}
```

### View API Documentation
Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Commands

### Run Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Create New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

### Format Code
```bash
black app/
```

### Lint Code
```bash
flake8 app/
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| BETTER_AUTH_SECRET | Yes | - | JWT secret key (32+ chars) |
| JWT_ALGORITHM | No | HS256 | JWT signing algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 15 | Access token expiration |
| REFRESH_TOKEN_EXPIRE_DAYS | No | 7 | Refresh token expiration |
| CORS_ORIGINS | Yes | - | Comma-separated allowed origins |
| ENVIRONMENT | No | development | Environment name |

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
- Verify DATABASE_URL is correct
- Check Neon database is running
- Ensure network connectivity

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Migration Errors
```bash
# Reset migrations (CAUTION: drops all data)
alembic downgrade base
alembic upgrade head
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Tasks
- `GET /api/v1/tasks` - Get all tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### Health
- `GET /api/v1/health` - Health check

## Development Tips

1. **Auto-reload**: Server automatically reloads on code changes
2. **API Docs**: Use `/docs` for interactive API testing
3. **Database**: Use Alembic for all schema changes
4. **Testing**: Write tests before implementing features (TDD)
5. **Security**: Never commit `.env` file

## Production Deployment

Before deploying to production:

1. Set `ENVIRONMENT=production` in `.env`
2. Use strong `BETTER_AUTH_SECRET` (generate with `openssl rand -hex 32`)
3. Update `CORS_ORIGINS` to production frontend URL
4. Enable HTTPS (cookies will use `secure=True` automatically)
5. Set up database backups
6. Configure error tracking (Sentry recommended)
7. Add rate limiting middleware
8. Run security audit: `pip-audit`

## Support

- Documentation: `/specs/001-fullstack-todo-app/`
- API Docs: http://localhost:8000/docs
- Audit Report: `backend/AUDIT_REPORT.md`
- Fixes Applied: `backend/FIXES_APPLIED.md`
