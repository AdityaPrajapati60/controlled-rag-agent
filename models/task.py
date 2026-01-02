# models/task.py
from sqlalchemy import Column, Integer, String
from db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    description = Column(String(2000), nullable=True)
    status = Column(String(50), default="pending", nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="tasks")

