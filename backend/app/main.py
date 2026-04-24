from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config import settings
from app.database import get_session
from app.middleware.security_headers import SecurityHeadersMiddleware
import sys


app = FastAPI(
    title="TaskFlow API",
    description="Full-stack todo application API",
    version="1.0.0",
)

# Security headers middleware (add first)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)


@app.get("/api/v1/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection
        await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        # Return 503 Service Unavailable when unhealthy
        from fastapi import Response
        from fastapi import status as http_status

        return Response(
            content='{"status":"unhealthy","database":"disconnected","error":"' + str(e) + '","environment":"' + settings.ENVIRONMENT + '"}',
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )


# Global flag to track database initialization
db_initialized = False


@app.on_event("startup")
async def startup_event():
    """Initialize database and start background services on startup"""
    global db_initialized
    from app.database import init_db
    from app.services.reminder_service import reminder_service
    from app.routes.notifications import manager
    import asyncio

    try:
        await init_db()
        db_initialized = True
        print("[OK] Database initialized successfully")

        # Connect reminder service to notification manager
        reminder_service.set_notification_manager(manager)

        # Start reminder service in background
        asyncio.create_task(reminder_service.run_reminder_loop())
        print("[OK] Reminder service started")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}", file=sys.stderr)
        db_initialized = False
        # Don't crash the app, but health check will report unhealthy


# Register routes
from app.routes import auth, tasks, notifications

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(notifications.router)
