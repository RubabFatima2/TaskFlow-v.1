from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.config import settings


# Convert PostgreSQL URL to async format and remove incompatible parameters
async_database_url = settings.DATABASE_URL

# Handle PostgreSQL-specific configuration
if "postgresql" in async_database_url:
    async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://")

    # Remove sslmode and channel_binding parameters (asyncpg doesn't support them in URL)
    # asyncpg uses ssl=True by default for secure connections
    if "?" in async_database_url:
        base_url, params = async_database_url.split("?", 1)
        # Remove sslmode and channel_binding from params
        param_list = [p for p in params.split("&") if not p.startswith("sslmode=") and not p.startswith("channel_binding=")]
        if param_list:
            async_database_url = f"{base_url}?{'&'.join(param_list)}"
        else:
            async_database_url = base_url

# Determine connect_args based on database type
connect_args = {}
engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
    "future": True,
}

if "postgresql" in async_database_url:
    connect_args = {"ssl": "require"}  # Enable SSL for PostgreSQL
    # PostgreSQL specific pooling settings
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    })
elif "sqlite" in async_database_url:
    connect_args = {"check_same_thread": False}  # SQLite-specific

engine_kwargs["connect_args"] = connect_args

# Create async engine
engine = create_async_engine(async_database_url, **engine_kwargs)

# Create async session factory
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session with proper error handling"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
