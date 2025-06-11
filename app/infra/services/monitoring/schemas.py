from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    STARTED = "STARTED"
    RETRY = "RETRY"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"
    QUEUED = "QUEUED"


class MergedTaskRecord(BaseModel):
    task_id: str
    name: str | None
    payload: dict | None
    created_at: datetime | None
    status: TaskStatus
    retries: int | None
    result: str | dict | bool | None
    traceback: str | None
    runtime: float | None
    queue: str | None
    worker: str | None
    completed_at: datetime | None
