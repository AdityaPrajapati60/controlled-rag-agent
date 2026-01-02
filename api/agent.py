# api/agent.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth_helpers import get_current_user
from db.database import SessionLocal
from agent.engine import run_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/run")
def run_agent_endpoint(
    prompt: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return run_agent(prompt, current_user, db)
