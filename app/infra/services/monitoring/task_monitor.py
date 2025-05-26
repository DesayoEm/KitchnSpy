from datetime import datetime, timezone, timedelta
from typing import List

from app.infra.db.adapters.task_adapter import TaskAdapter
from app.infra.log_service import logger
from app.infra.services.monitoring.schemas import TaskStatus, TaskStatusResponse
from app.shared.serializer import Serializer


class TaskMonitoringService:
    def __init__(self):
        """Service for monitoring and managing Celery task results."""
        self.db = TaskAdapter()
        self.serializer = Serializer()

    def find_task(self, task_id: str) -> TaskStatusResponse:
        task = self.db.find_task_by_id(task_id)
        return TaskStatusResponse.model_validate(task)


    def filter_tasks_by_type_and_date(
            self, start_date: datetime,
            end_date: datetime,
            status: TaskStatus,
            per_page: int
        ) -> List[TaskStatusResponse]:

        """Return tasks within a date range filtered by status."""
        query = {
            "date_done": {
                "$gte": start_date,
                "$lte": end_date
            },
            "status": status.value
        }
        tasks = self.db.filter_tasks(query, per_page)
        return [TaskStatusResponse.model_validate(task) for task in tasks]


    def retry_task(self, task_id: str) -> None:
        """Retry a specific task by ID."""
        pass

    def retry_tasks(self) -> None:
        """Retry failed tasks in bulk."""
        pass

    def purge_old_tasks(self, status: TaskStatus) -> str:
        """Delete tasks older than a fixed time window"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)
        result = self.db.tasks.delete_many({
            "date_done": {"$lt": cutoff_date},
            "status": status.value
        })
        deleted_count = result.deleted_count
        logger.info(f"{deleted_count} old {status.value} tasks deleted")
        return f"Deleted {deleted_count} {status.value} tasks"


    def count_tasks(self) -> str:
        """Count all tasks in the collection."""
        result = self.db.tasks.count_documents({})
        return f"{result} tasks found"


    def count_filtered_tasks(self, start_date: datetime, end_date: datetime, status: TaskStatus) -> str:
        """Count tasks within a date range filtered by status."""
        query = {
            "date_done": {
                "$gte": start_date,
                "$lte": end_date
            },
            "status": status.value
        }
        result = self.db.tasks.count_documents(query)
        return f"{result} {status} tasks found"

