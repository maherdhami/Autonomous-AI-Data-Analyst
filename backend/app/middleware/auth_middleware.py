from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.core.firebase import verify_firebase_token
from app.database.firestore import db_repo
from app.schemas.auth import UserResponse

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    if not credentials:
        # For development / initial testing mode fallback user
        return UserResponse(
            user_id="default_dev_user",
            name="Demo Analyst",
            email="demo@enterprise.com",
            role="admin",
            created_at=1700000000,
            last_login=1700000000,
            subscription="enterprise"
        )
        
    token = credentials.credentials
    user_data = None
    
    # 1. Try internal JWT
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        user_id = payload["sub"]
        doc = db_repo.get_document("users", user_id)
        if doc:
            return UserResponse(**doc)
        user_data = {
            "user_id": user_id,
            "name": payload.get("name", "User"),
            "email": payload.get("email", f"{user_id}@example.com"),
            "role": payload.get("role", "user"),
            "created_at": payload.get("iat", 1700000000),
            "last_login": 1700000000
        }
        return UserResponse(**user_data)
        
    # 2. Try Firebase ID Token
    try:
        firebase_payload = verify_firebase_token(token)
        uid = firebase_payload.get("uid")
        email = firebase_payload.get("email", f"{uid}@example.com")
        doc = db_repo.get_document("users", uid)
        if doc:
            return UserResponse(**doc)
            
        user_dict = {
            "user_id": uid,
            "name": firebase_payload.get("name", email.split("@")[0]),
            "email": email,
            "role": "admin" if email.endswith("@admin.com") else "user",
            "created_at": 1700000000,
            "last_login": 1700000000,
            "subscription": "free"
        }
        db_repo.set_document("users", uid, user_dict)
        return UserResponse(**user_dict)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def require_admin(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
