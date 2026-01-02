from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from db.database import Base

class PlannerPlan(Base):
    __tablename__ = "planner_plans"

    id = Column(Integer, primary_key=True)

    run_id = Column(
        Integer,
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
    )

    step_index = Column(Integer, nullable=False)
    tool_name = Column(String, nullable=False)
    tool_args = Column(JSON, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="pending",  # pending | executed | skipped | error
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
