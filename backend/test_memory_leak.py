from app.models.message import Message
from sqlmodel import SQLModel

print(Message.model_fields['role'].json_schema_extra)
