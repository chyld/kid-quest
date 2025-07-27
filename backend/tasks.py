from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Dict, Any
from fastapi import HTTPException
from db import get_task_by_id, update_task_status

class Task(BaseModel):
    title: str
    reward: int
    created_at: datetime = datetime.now()
    status: Literal["pending", "working", "done"] = "pending"

class TaskAction(BaseModel):
    action: Literal["start", "finish"]

def update_reward_total(reward_amount: int) -> None:
    """Update the total reward in reward.txt by adding the given amount."""
    try:
        with open("reward.txt", "r") as f:
            current_total = int(f.read().strip())
        
        new_total = current_total + reward_amount
        
        with open("reward.txt", "w") as f:
            f.write(str(new_total))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update reward total: {e}")

def process_task_status_update(task_id: int, action: TaskAction) -> Dict[str, Any]:
    """Process task status update with business logic and reward handling."""
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    current_status = task["status"]
    new_status = current_status

    if action.action == "start":
        if current_status == "pending":
            new_status = "working"
        else:
            raise HTTPException(status_code=400, detail=f"Cannot start a task with status '{current_status}'. Only 'pending' tasks can be started.")
    elif action.action == "finish":
        if current_status == "working":
            new_status = "done"
        else:
            raise HTTPException(status_code=400, detail=f"Cannot finish a task with status '{current_status}'. Only 'working' tasks can be finished.")

    updated = update_task_status(task_id, new_status)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update task status.")

    # Add task reward to total reward when task is finished
    if action.action == "finish" and new_status == "done":
        update_reward_total(task["reward"])

    return {"message": f"Task status updated to '{new_status}'", "task_id": task_id, "new_status": new_status}
