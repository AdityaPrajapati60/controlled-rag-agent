# api/admin_guard.py
from fastapi import HTTPException

def require_admin(user):
    role = getattr(user, "role", "user")
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
