#models/agent_action
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from db.database import Base

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(Integer, primary_key=True)

    run_id = Column(
        Integer,
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
    )

    tool_name = Column(String, nullable=False)
    tool_input = Column(String, nullable=True)
    tool_output = Column(String, nullable=True)

    status = Column(
        String,
        nullable=False,
        default="success",  # success | error | skipped
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
