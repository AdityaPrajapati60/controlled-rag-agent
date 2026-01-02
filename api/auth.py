# api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from db.database import SessionLocal
from models.user import User
from models.schemas import UserCreate, UserResponse, Token
from core.security import get_password_hash, verify_password, create_access_token
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Swagger sends form fields (username,password). Fill `username` with the user's email.
    """
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
         subject=str(user.id),
         expires_delta=access_token_expires,
         additional_claims={"role": user.role}
    )
    return {"access_token": token, "token_type": "bearer"}
