from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from networking import NetworkingState, control_networking
from tasks import Task, TaskAction, process_task_status_update
from db import create_db_and_tables, insert_task, get_all_tasks, get_task_by_id, update_task, delete_task, update_task_status, dump_tasks_to_csv

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

@app.post("/networking")
async def networking_endpoint(networking_state: NetworkingState):
    return await control_networking(networking_state)

@app.get("/reward")
async def get_current_reward():
    try:
        with open("reward.txt", "r") as f:
            current_reward = int(f.read().strip())
        return {"total_reward": current_reward}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read reward: {e}")

@app.put("/reward")
async def update_reward(new_value: int):
    try:
        with open("reward.txt", "w") as f:
            f.write(str(new_value))
        return {"message": "Reward updated successfully", "new_total": new_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update reward: {e}")

@app.post("/tasks/")
async def create_task(task: Task):
    task_id = insert_task(task.title, task.reward, task.created_at, task.status)
    return {"id": task_id, **task.dict()}

@app.get("/tasks/")
async def get_tasks(status: Union[str, None] = None):
    tasks = get_all_tasks(status)
    return tasks

@app.get("/tasks/dump-csv")
async def dump_csv_endpoint():
    csv_data = dump_tasks_to_csv()
    response = StreamingResponse(iter([csv_data]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=tasks.csv"
    return response

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}")
async def update_task_endpoint(task_id: int, task: Task):
    updated = update_task(task_id, task.title, task.reward, task.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated successfully", "task": {"id": task_id, **task.dict()}}

@app.delete("/tasks/{task_id}")
async def delete_task_endpoint(task_id: int):
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@app.put("/tasks/{task_id}/status")
async def update_task_status_endpoint(task_id: int, action: TaskAction):
    return process_task_status_update(task_id, action)
