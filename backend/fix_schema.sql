ALTER TABLE messages DROP CONSTRAINT messages_role_check;
ALTER TABLE messages ADD CONSTRAINT messages_role_check CHECK (role IN ('user', 'assistant', 'tool'));
ALTER TABLE messages ADD COLUMN IF NOT EXISTS tool_call_id VARCHAR(255);
