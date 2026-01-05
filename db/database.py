# db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --------------------------------------------------
# Database URL resolution (SAFE FOR RENDER + LOCAL)
# --------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite for local / free-tier deployment
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app.db"

# --------------------------------------------------
# SQLAlchemy setup
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()