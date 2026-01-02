from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from db.database import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    input = Column(String, nullable=False)
    output = Column(String, nullable=True)

    estimated_tokens_used = Column(Integer, nullable=False, default=0)
    budget_exceeded = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
