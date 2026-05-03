import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def apply():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_role_check;"))
        except Exception as e:
            print("Drop constraint failed:", e)
        
        try:
            await conn.execute(text("ALTER TABLE messages ADD CONSTRAINT messages_role_check CHECK (role IN ('user', 'assistant', 'tool'));"))
        except Exception as e:
            print("Add constraint failed:", e)
            
        await conn.execute(text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS tool_call_id VARCHAR(255);"))
        print("Schema updated successfully.")

asyncio.run(apply())
