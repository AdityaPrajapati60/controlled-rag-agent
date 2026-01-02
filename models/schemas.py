# app/models/schemas.py
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator("title")
    def strip_and_not_empty(cls, v: str):
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("title cannot be empty or whitespace")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None

    @validator("title")
    def non_empty_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError("title cannot be empty or whitespace")
        return v.strip() if v is not None else v

#These define the data returned from the API to the user.
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=200)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True




class PrioritizedTask(BaseModel):
    """Schema for the AI to return a single prioritized task."""
    id: int = Field(..., description="The original database ID of the task.")
    title: str = Field(..., description="The title of the task.")
    priority_score: int = Field(..., ge=1, le=10, description="A score from 1 (lowest) to 10 (highest priority).")
    justification: str = Field(..., description="A one-sentence reason for this priority score.")

class PrioritySuggestion(BaseModel):
    """Schema for the complete AI priority response."""
    # This list will hold the structured tasks returned by the LLM
    prioritized_tasks:List[PrioritizedTask]