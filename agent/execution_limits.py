from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.agent_run import AgentRun


class AgentRateLimitError(Exception):
    """Raised when an agent exceeds allowed execution limits"""
    pass


MAX_RUNS = 20
WINDOW_MINUTES = 10


def enforce_run_limit(db: Session, user_id: int):
    cutoff = datetime.utcnow() - timedelta(minutes=WINDOW_MINUTES)

    count = (
        db.query(AgentRun)
        .filter(
            AgentRun.user_id == user_id,
            AgentRun.created_at >= cutoff,
        )
        .count()
    )

    if count >= MAX_RUNS:
        raise AgentRateLimitError(
            "Agent rate limit exceeded. Please wait before making more requests."
        )

