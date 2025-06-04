from fastapi import APIRouter
from datetime import date

from app.infra.services.monitoring.schemas import TaskStatus
from app.infra.services.monitoring.task_monitor import TaskMonitoringService
from app.infra.db.adapters.task_adapter import TaskAdapter
from fastapi.responses import StreamingResponse
import json


router = APIRouter()
task_adapter = TaskAdapter()
task_monitor = TaskMonitoringService()


@router.get("/tasks/filter")
def get_tasks(start_date, end_date, status):
    return task_monitor.filter_tasks_by_type_and_date(start_date, end_date, status)

@router.get("/tasks/count")
def count_all_tasks():
    return task_monitor.count_tasks()

@router.get("/tasks/filtered_count")
def count_filtered_tasks(start_date: date, end_date: date, status: TaskStatus):
    return task_monitor.count_filtered_tasks(start_date, end_date, status)

@router.post("/tasks/retry", status_code=201)
def retry_tasks(start_date: date, end_date: date):
    return task_monitor.retry_failed_tasks(start_date, end_date)

@router.post("/tasks/{task_id}/retry", status_code=201)
def retry_task(task_id: str):
    return task_monitor.retry_failed_task(task_id)

@router.get("/tasks/{task_id}")
def get_task_detail(task_id: str):
    return task_monitor.get_task_detail(task_id)

@router.delete("/tasks/{task_id}", status_code=204)
def purge_tasks(status: TaskStatus):
    return task_monitor.purge_old_tasks(status)

@router.delete("/tasks/purge", status_code=204)
def delete_task(task_id: str):
    return task_adapter.delete_task(task_id)
