import logging
from datetime import datetime
from models.auth import UserSignup, UserLogin, UserResponse
from fastapi import APIRouter, HTTPException
from utils.authUtils import load_users, generate_user_id, hash_password, save_users, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Invalid Username or Password"}},
)

@router.post("/signup")
def signup(user_data: UserSignup):
    """Register a new user"""
    users = load_users()
    
    # Check if user already exists
    if any(user["email"] == user_data.email for user in users.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if phone already exists
    if any(user["phone"] == user_data.phone for user in users.values()):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create new user
    user_id = generate_user_id(user_data.email)
    new_user = {
        "id": user_id,
        "name": user_data.name,
        "email": user_data.email,
        "phone": user_data.phone,
        "password": hash_password(user_data.password),
        "created_at": datetime.now().isoformat()
    }
    
    # Save user
    users[user_id] = new_user
    save_users(users)
    
    # Return user data (without password)
    user_response = UserResponse(
        id=new_user["id"],
        name=new_user["name"],
        email=new_user["email"],
        phone=new_user["phone"],
        created_at=new_user["created_at"]
    )
    
    return {
        "message": "User registered successfully",
        "user": user_response.dict()
    }

@router.post("/login")
def login(user_credentials: UserLogin):
    """Authenticate user login"""
    users = load_users()
    
    # Find user by email
    user = None
    for user_data in users.values():
        if user_data["email"] == user_credentials.email:
            user = user_data
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Return user data (without password)
    user_response = UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        phone=user["phone"],
        created_at=user["created_at"]
    )
    
    return {
        "message": "Login successful",
        "user": user_response.dict(),
        "token": f"token_{user['id']}"  # Simple token for demo
    }