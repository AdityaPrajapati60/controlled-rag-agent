# api/auth_helpers.py 

from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status 
from fastapi.security import OAuth2PasswordBearer
from db.database import SessionLocal
from models.user import User as UserModel 
from core.config import SECRET_KEY, ALGORITHM

# ----------------------------------------------------
# 1. Define the OAuth2 Scheme
# ----------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") 

def get_current_user(token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        role = payload.get("role")

        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # 🔑 Inject role from token
        user.role = role
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token validation error")

    finally:
        db.close()
