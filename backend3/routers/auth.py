import logging
from schemas.auth_schema import AdminLogin, UserLogin
from fastapi import APIRouter, HTTPException
from services.auth_service import create_user_if_not_exist

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Invalid Username or Password"}},
)

admin_email = "admin@gmail.com"
admin_password = "Admin@123"

@router.post("/admin_login")
def login_admin(admin_credentials: AdminLogin):
    """Authenticate admin login with hardcoded credentials"""

    if admin_credentials.email != admin_email or admin_credentials.password != admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    return {
        "message": "Login successful",
    }

@router.post("/user_login")
def login_user(user_credentials: UserLogin):
    """Login using only phone number (no password)"""

    phone = user_credentials.phone
    user = create_user_if_not_exist(phone)

    return {
        "message": "Access granted successfully",
        "user": user
    }
