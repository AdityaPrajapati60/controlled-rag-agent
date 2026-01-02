# api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import SessionLocal
# Import the User model to get current_user.id
from models.user import User as UserModel 
from models.task import Task
from models.schemas import TaskCreate, TaskResponse, TaskUpdate
from api.auth_helpers import get_current_user  # current-user helper

router = APIRouter(tags=["tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------------------------
# 1. CREATE TASK (POST) - SECURED AND USER-SPECIFIC
# ----------------------------------------------------------------------
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    # Dependency runs first: checks JWT and returns the User object
    current_user: UserModel = Depends(get_current_user), 
):
    # CRITICAL: Link the new task to the authenticated user's ID
    new = Task(**payload.dict(), user_id=current_user.id)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# ----------------------------------------------------------------------
# 2. LIST TASKS (GET /tasks) - SECURED AND USER-SPECIFIC
# ----------------------------------------------------------------------
@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user),
    limit: int = 10, 
    offset: int = 0
):
    # CRITICAL: Filter tasks by the authenticated user's ID
    return (
        db.query(Task)
        .filter(Task.user_id == current_user.id)
        .order_by(Task.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

# ----------------------------------------------------------------------
# 3. GET SINGLE TASK (GET /tasks/{id}) - SECURED AND USER-SPECIFIC
# ----------------------------------------------------------------------
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    # CRITICAL: Filter by both Task ID AND User ID
    t = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    # 404 is used to hide the existence of tasks belonging to other users
    if not t:
        raise HTTPException(status_code=404, detail="Task not found") 
    return t

# ----------------------------------------------------------------------
# 4. UPDATE TASK (PUT) - SECURED AND USER-SPECIFIC
# ----------------------------------------------------------------------
@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, 
    payload: TaskUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    # CRITICAL: Filter by both Task ID AND User ID
    t = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update logic (only update fields that were provided in the payload)
    if payload.title is not None:
        t.title = payload.title.strip()
    if payload.description is not None:
        t.description = payload.description
    if payload.status is not None:
        # Pydantic enum value is extracted correctly
        t.status = payload.status.value 
        
    db.commit()
    db.refresh(t)
    return t

# ----------------------------------------------------------------------
# 5. DELETE TASK (DELETE) - SECURED AND USER-SPECIFIC
# ----------------------------------------------------------------------
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    # CRITICAL: Filter by both Task ID AND User ID
    t = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(t)
    db.commit()
    return