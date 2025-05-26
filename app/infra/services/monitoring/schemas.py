from enum import Enum
from pydantic import BaseModel

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    STARTED = "STARTED"
    RETRY = "RETRY"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"

class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: str | None
    error: str | None

