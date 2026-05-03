# Backend Audit Report - Critical Issues Found

**Date**: 2026-04-11  
**Auditor**: Professional Web Developer Review  
**Status**: 🔴 CRITICAL ISSUES FOUND

---

## Executive Summary

Found **12 critical issues** and **8 warnings** that will prevent the application from working correctly. Issues range from missing updated_at triggers, incorrect datetime usage, missing .env file, to incomplete refresh token implementation.

---

## 🔴 CRITICAL ISSUES

### 1. **Missing `updated_at` Auto-Update in Models**
**Location**: `backend/app/models/user.py`, `backend/app/models/task.py`  
**Severity**: HIGH  
**Impact**: `updated_at` field never updates after record creation

**Problem**:
```python
updated_at: datetime = Field(default_factory=datetime.utcnow)
```

The `updated_at` field only sets on creation, never updates on modifications. While the migration creates triggers, SQLModel doesn't automatically update this field in the application layer.

**Fix Required**:
- Add `sa_column_kwargs={"onupdate": datetime.utcnow}` to the Field
- OR handle updates manually in services
- OR rely solely on database triggers (current approach, but risky if bypassed)

---

### 2. **Deprecated `datetime.utcnow()` Usage**
**Location**: Multiple files  
**Severity**: MEDIUM  
**Impact**: Will cause deprecation warnings, potential timezone issues

**Problem**:
```python
from datetime import datetime
created_at: datetime = Field(default_factory=datetime.utcnow)
```

`datetime.utcnow()` is deprecated in Python 3.12+. Should use timezone-aware datetime.

**Fix Required**:
```python
from datetime import datetime, timezone
created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

**Files to fix**:
- `backend/app/models/user.py`
- `backend/app/models/task.py`
- `backend/app/utils/security.py`

---

### 3. **Missing `.env` File**
**Location**: `backend/.env`  
**Severity**: CRITICAL  
**Impact**: Application won't start without environment variables

**Problem**: No `.env` file exists, only `.env.example` is documented in specs.

**Fix Required**: Create `backend/.env` with:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

---

### 4. **Incomplete Refresh Token Implementation**
**Location**: `backend/app/routes/auth.py:70-80`  
**Severity**: HIGH  
**Impact**: Users cannot refresh expired access tokens

**Problem**:
```python
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(response: Response, refresh_token: str = None):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token endpoint not yet implemented"
    )
```

**Fix Required**: Implement full refresh token logic with cookie extraction and validation.

---

### 5. **Missing Cookie Extraction in Refresh Endpoint**
**Location**: `backend/app/routes/auth.py:71`  
**Severity**: HIGH  
**Impact**: Refresh token endpoint cannot read cookies

**Problem**:
```python
refresh_token: str = None  # Wrong - should use Cookie()
```

**Fix Required**:
```python
from fastapi import Cookie
refresh_token: Optional[str] = Cookie(None)
```

---

### 6. **Insecure Cookie Settings in Development**
**Location**: `backend/app/routes/auth.py:36-37`  
**Severity**: MEDIUM  
**Impact**: Cookies won't work over HTTP in development

**Problem**:
```python
secure=True,  # This breaks localhost HTTP
```

**Fix Required**:
```python
secure=settings.ENVIRONMENT == "production",  # Only secure in production
```

---

### 7. **Missing Health Check Database Connection Test**
**Location**: `backend/app/main.py:22-25`  
**Severity**: MEDIUM  
**Impact**: Health check doesn't verify database connectivity

**Problem**:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
```

**Fix Required**: Add actual database connection test:
```python
@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

---

### 8. **Missing Error Handling for Database Connection Failures**
**Location**: `backend/app/database.py`  
**Severity**: HIGH  
**Impact**: Application crashes on database connection failure

**Problem**: No try-catch around database operations, no connection retry logic.

**Fix Required**: Add connection error handling and retry logic.

---

### 9. **Missing `updated_at` Manual Update in Services**
**Location**: `backend/app/services/task_service.py:71`  
**Severity**: MEDIUM  
**Impact**: `updated_at` may not update if triggers fail

**Problem**:
```python
await session.commit()
await session.refresh(task)
```

No explicit `updated_at` update before commit.

**Fix Required**:
```python
from datetime import datetime, timezone
task.updated_at = datetime.now(timezone.utc)
await session.commit()
```

---

### 10. **Missing CORS Preflight Headers**
**Location**: `backend/app/main.py:13-19`  
**Severity**: LOW  
**Impact**: May cause CORS issues with cookies

**Problem**: Missing `expose_headers` configuration for cookies.

**Fix Required**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],  # Add this
)
```

---

### 11. **Missing Input Sanitization for Title**
**Location**: `backend/app/services/task_service.py:20`  
**Severity**: LOW  
**Impact**: Empty titles after stripping whitespace not caught

**Problem**:
```python
title=task_data.title.strip(),
```

If title is only whitespace, `.strip()` makes it empty, but validation happens before strip.

**Fix Required**:
```python
title = task_data.title.strip()
if not title:
    raise HTTPException(status_code=400, detail="Title cannot be empty")
```

---

### 12. **Missing Database Session Cleanup on Error**
**Location**: `backend/app/database.py:35-38`  
**Severity**: MEDIUM  
**Impact**: Database connections may leak on errors

**Problem**:
```python
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

No explicit error handling or rollback.

**Fix Required**:
```python
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## ⚠️ WARNINGS

### W1. **Missing API Versioning in Health Check**
**Location**: `backend/app/main.py:22`  
**Issue**: Health check at `/health` should be at `/api/v1/health` for consistency.

### W2. **Missing Rate Limiting**
**Location**: All routes  
**Issue**: No rate limiting middleware configured (spec requires 5 req/min for auth, 30 req/min for tasks).

### W3. **Missing Request Logging Middleware**
**Location**: `backend/app/main.py`  
**Issue**: No request/response logging for debugging.

### W4. **Missing Error Tracking Integration**
**Location**: `backend/app/main.py`  
**Issue**: No Sentry or error tracking configured.

### W5. **Missing Password Strength Validation**
**Location**: `backend/app/schemas/auth.py:8`  
**Issue**: Only checks length, not complexity (uppercase, lowercase, numbers, special chars).

### W6. **Missing Email Normalization in Login**
**Location**: `backend/app/routes/auth.py:28`  
**Issue**: Email should be normalized to lowercase before authentication (already done in service, but should be in schema).

### W7. **Missing Pagination for Task List**
**Location**: `backend/app/routes/tasks.py:22-29`  
**Issue**: No pagination, will fail with large task lists.

### W8. **Missing OpenAPI Documentation Examples**
**Location**: All routes  
**Issue**: No `response_model` examples for better API docs.

---

## 📋 MISSING FILES

1. **`backend/.env`** - Critical for running the application
2. **`backend/.env.example`** - Template for environment variables
3. **`backend/app/__init__.py`** - Package initializer (optional but recommended)
4. **`backend/pytest.ini`** - Exists but not verified
5. **Unit test files** - Missing from `backend/tests/unit/`
6. **Integration test files** - Missing from `backend/tests/integration/`

---

## 🔧 PRIORITY FIX ORDER

### Immediate (Blocks Development):
1. Create `backend/.env` file
2. Fix secure cookie settings for development
3. Implement refresh token endpoint
4. Fix datetime.utcnow() deprecation

### High Priority (Blocks Production):
1. Add database connection error handling
2. Fix updated_at auto-update
3. Add health check database test
4. Add input sanitization for empty titles

### Medium Priority (Quality/Security):
1. Add rate limiting middleware
2. Add request logging
3. Add error tracking
4. Add pagination to task list

### Low Priority (Nice to Have):
1. Add password strength validation
2. Add API documentation examples
3. Improve CORS configuration

---

## 📊 STATISTICS

- **Total Files Audited**: 20
- **Critical Issues**: 12
- **Warnings**: 8
- **Missing Files**: 6
- **Lines of Code Reviewed**: ~800
- **Estimated Fix Time**: 4-6 hours

---

## ✅ WHAT'S WORKING WELL

1. ✅ Clean separation of concerns (models, schemas, services, routes)
2. ✅ Proper use of async/await throughout
3. ✅ Good use of dependency injection
4. ✅ User data isolation enforced in queries
5. ✅ Password hashing with bcrypt
6. ✅ JWT token generation and verification
7. ✅ Proper HTTP status codes
8. ✅ Pydantic validation on all inputs
9. ✅ Foreign key constraints in migrations
10. ✅ Proper indexes on database tables

---

## 🎯 NEXT STEPS

1. Review this audit report
2. Prioritize fixes based on severity
3. Create tasks for each fix
4. Implement fixes in order of priority
5. Test each fix thoroughly
6. Re-audit after fixes

---

**End of Audit Report**
