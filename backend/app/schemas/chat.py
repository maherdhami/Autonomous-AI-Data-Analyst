from typing import Optional, List, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str
    code: Optional[str] = None
    execution_result: Optional[Any] = None
    timestamp: int

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    file_id: Optional[str] = None
    question: str
    mode: str = "strategic" # "strategic" or "code"
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessage


