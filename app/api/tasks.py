from fastapi import APIRouter, Query
from app.infra.db.adapters.task_adapter import TaskAdapter
from fastapi.responses import StreamingResponse
import json

router = APIRouter()
task_adapter = TaskAdapter()


@router.get("/tasks/failed")
def get_failed_tasks():
    return task_adapter.find_failed_tasks()

@router.get("/tasks/recent")
def get_tasks(start_date, end_date, status):
    return task_adapter.find_tasks(start_date, end_date, status)

@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = task_adapter.find_task_by_id(task_id)
    return {
        "status": task.get("status"),
        "result": task.get("result"),
        "date_done": task.get("date_done"),
        "traceback": task.get("traceback"),
    }

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    return task_adapter.delete_task(task_id)