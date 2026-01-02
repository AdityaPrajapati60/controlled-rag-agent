# agent/task_tools
from sqlalchemy.orm import Session
from models.task import Task

def get_tasks(db: Session, user_id: int):
    tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .order_by(Task.id.desc())
        .all()
    )

    return [
        {"id": t.id, "title": t.title, "status": t.status}
        for t in tasks
    ]


def create_task(db: Session, user_id: int, title: str, description: str | None):
    task = Task(
        title=title,
        description=description,
        user_id=user_id,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
    }
