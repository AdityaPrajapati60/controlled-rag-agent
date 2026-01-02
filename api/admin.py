from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from db.database import SessionLocal
from api.auth_helpers import get_current_user
from api.admin_guard import require_admin

from models.agent_run import AgentRun
from models.agent_action import AgentAction

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────
# 🔍 VIEW ALL AGENT RUNS
# ─────────────────────────────────────
@router.get("/agent-runs")
def list_agent_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_admin(current_user)

    runs = (
        db.query(AgentRun)
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "input": r.input,
            "output": r.output,
            "created_at": r.created_at,
        }
        for r in runs
    ]


# ─────────────────────────────────────
# 🔎 VIEW ACTIONS FOR A RUN
# ─────────────────────────────────────
@router.get("/agent-runs/{run_id}/actions")
def list_agent_run_actions(
    run_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_admin(current_user)

    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")

    actions = (
        db.query(AgentAction)
        .filter(AgentAction.run_id == run_id)
        .order_by(AgentAction.created_at.asc())
        .all()
    )

    return {
        "run_id": run_id,
        "input": run.input,
        "output": run.output,
        "actions": [
            {
                "id": a.id,
                "tool_name": a.tool_name,
                "tool_input": a.tool_input,
                "tool_output": a.tool_output,
                "created_at": a.created_at,
            }
            for a in actions
        ],
    }


# ─────────────────────────────────────
# 🧹 CLEANUP OLD LOGS
# ─────────────────────────────────────
@router.delete("/cleanup-agent-logs")
def cleanup_agent_logs(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_admin(current_user)

    cutoff = datetime.utcnow() - timedelta(days=days)

    deleted_actions = (
        db.query(AgentAction)
        .filter(AgentAction.created_at < cutoff)
        .delete(synchronize_session=False)
    )

    deleted_runs = (
        db.query(AgentRun)
        .filter(AgentRun.created_at < cutoff)
        .delete(synchronize_session=False)
    )

    db.commit()

    return {
        "status": "success",
        "deleted_agent_actions": deleted_actions,
        "deleted_agent_runs": deleted_runs,
        "older_than_days": days,
    }
