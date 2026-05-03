from sqlalchemy import create_engine, text
from app.config import settings

def apply():
    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_role_check;"))
            print("Dropped constraint.")
        except Exception as e:
            print("Drop constraint failed:", e)
        
        try:
            conn.execute(text("ALTER TABLE messages ADD CONSTRAINT messages_role_check CHECK (role IN ('user', 'assistant', 'tool'));"))
            print("Added constraint.")
        except Exception as e:
            print("Add constraint failed:", e)
            
        try:
            conn.execute(text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS tool_call_id VARCHAR(255);"))
            print("Added column.")
        except Exception as e:
            print("Add column failed:", e)
        
        print("Schema updated successfully.")

apply()
