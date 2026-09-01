from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr

class UserModel(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    hashed_password: Optional[str] = None
    role: str = "user" # "admin" | "user"
    subscription: str = "free"
    created_at: int
    last_login: int
    preferences: Dict[str, Any] = Field(default_factory=dict)
