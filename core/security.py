# core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    if password is None:
        raise ValueError("password required")

    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]

    return pwd_context.hash(pw_bytes)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password is None:
        return False

    pw_bytes = plain_password.encode("utf-8")
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]

    return pwd_context.verify(pw_bytes, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta, additional_claims: dict | None = None):
    to_encode = {"sub": subject}
    if additional_claims:
        to_encode.update(additional_claims)

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
