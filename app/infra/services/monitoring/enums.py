from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    STARTED = "STARTED"
    RETRY = "RETRY"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"