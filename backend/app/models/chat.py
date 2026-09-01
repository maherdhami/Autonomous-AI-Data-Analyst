from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class MessageModel(BaseModel):
    message_id: str
    session_id: str
    role: str # "user" or "assistant"
    content: str
    code: Optional[str] = None
    execution_result: Optional[Any] = None
    timestamp: int

class ChatSessionModel(BaseModel):
    session_id: str
    user_id: str
    file_id: Optional[str] = None
    created_at: int
    updated_at: int
