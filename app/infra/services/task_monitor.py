from datetime import datetime, timezone, timedelta
from bson import ObjectId
from app.infra.db.adapters.task_adapter import TaskAdapter
from typing import Iterator
from app.infra.log_service import logger
from app.shared.serializer import Serializer


class TaskMonitoringService:
    def __init__(self):
        """
        Initialize TaskMonitoringService with database access
        """
        self.db = TaskAdapter()
        self.serializer = Serializer()

    def retry_task(self, task_id: str):
        pass

    def retry_tasks(self):
        pass

    def purge_old_tasks(self):
        pass

    def count_errors(self):
        pass

    def schedule_cleanups(self):
        pass

