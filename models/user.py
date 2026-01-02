# models/user.py
from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(String(20), nullable=False, default="user")  # 👈 NEW

    is_active = Column(Boolean, default=True, nullable=False)

    tasks = relationship("Task", back_populates="user")
