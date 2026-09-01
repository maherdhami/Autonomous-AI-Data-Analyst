import time
import uuid
from fastapi import APIRouter, HTTPException, Depends, status
# pyrefly: ignore [missing-import]
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    FirebaseTokenAuthRequest,
    UserResponse,
    TokenResponse
)
from app.schemas.common import ResponseModel
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.firebase import verify_firebase_token
from app.database.firestore import db_repo
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

@router.post("/register", response_model=ResponseModel[TokenResponse])
async def register_user(req: UserRegisterRequest):
    # Check if email exists
    existing = db_repo.query_collection("users", field="email", value=req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )
        
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    now = int(time.time())
    user_dict = {
        "user_id": user_id,
        "name": req.name,
        "email": req.email,
        "hashed_password": get_password_hash(req.password),
        "role": "admin" if req.email.startswith("admin@") else "user",
        "subscription": "free",
        "created_at": now,
        "last_login": now,
        "preferences": {}
    }
    
    db_repo.set_document("users", user_id, user_dict)
    
    token = create_access_token(user_id, extra_claims={"name": req.name, "email": req.email, "role": user_dict["role"]})
    user_res = UserResponse(**user_dict)
    
    return ResponseModel(
        success=True,
        message="User registered successfully",
        data=TokenResponse(access_token=token, user=user_res)
    )

@router.post("/login", response_model=ResponseModel[TokenResponse])
async def login_user(req: UserLoginRequest):
    existing = db_repo.query_collection("users", field="email", value=req.email)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    user_data = existing[0]
    if not user_data.get("hashed_password") or not verify_password(req.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    user_data["last_login"] = int(time.time())
    db_repo.set_document("users", user_data["user_id"], user_data)
    
    token = create_access_token(
        user_data["user_id"],
        extra_claims={"name": user_data["name"], "email": user_data["email"], "role": user_data.get("role", "user")}
    )
    user_res = UserResponse(**user_data)
    
    return ResponseModel(
        success=True,
        message="Login successful",
        data=TokenResponse(access_token=token, user=user_res)
    )

@router.post("/firebase", response_model=ResponseModel[TokenResponse])
async def firebase_auth(req: FirebaseTokenAuthRequest):
    try:
        fb_user = verify_firebase_token(req.id_token)
        uid = fb_user.get("uid")
        email = fb_user.get("email", f"{uid}@firebase.com")
        name = fb_user.get("name", email.split("@")[0])
        
        doc = db_repo.get_document("users", uid)
        now = int(time.time())
        if not doc:
            doc = {
                "user_id": uid,
                "name": name,
                "email": email,
                "role": "admin" if email.startswith("admin@") else "user",
                "subscription": "free",
                "created_at": now,
                "last_login": now,
                "preferences": {}
            }
        else:
            doc["last_login"] = now
            
        db_repo.set_document("users", uid, doc)
        token = create_access_token(uid, extra_claims={"name": name, "email": email, "role": doc["role"]})
        user_res = UserResponse(**doc)
        
        return ResponseModel(
            success=True,
            message="Firebase authentication successful",
            data=TokenResponse(access_token=token, user=user_res)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Firebase token verification failed: {str(e)}")

@router.post("/logout", response_model=ResponseModel[bool])
async def logout(current_user: UserResponse = Depends(get_current_user)):
    return ResponseModel(success=True, message="Logout successful", data=True)

@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return ResponseModel(success=True, message="Current user retrieved", data=current_user)
