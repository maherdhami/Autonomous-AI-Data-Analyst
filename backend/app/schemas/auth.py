from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class FirebaseTokenAuthRequest(BaseModel):
    id_token: str

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: str = "user"
    created_at: int
    last_login: int
    subscription: str = "free"
    preferences: Dict[str, Any] = {}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
