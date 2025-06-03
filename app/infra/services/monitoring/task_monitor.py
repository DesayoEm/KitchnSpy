from datetime import datetime, timezone, timedelta
from typing import List

from app.domain.price_logs.services.notification_service.tasks import send_price_email_notification
from app.domain.products.services.notification_service.tasks import send_product_email_notification
from app.domain.subscribers.services.notification_service.tasks import send_subscription_email_notification

from app.infra.db.adapters.task_adapter import TaskAdapter
from app.infra.log_service import logger
from app.infra.services.monitoring.schemas import TaskStatus, MergedTaskRecord
from app.shared.exceptions import NotFailedTaskError
from app.shared.serializer import Serializer


TASK_MAP = {
    "product_removed": send_product_email_notification,
    "price_change": send_price_email_notification,
    "subscription_notification": send_subscription_email_notification,

}
class TaskMonitoringService:
    def __init__(self):
        """Service for monitoring and managing Celery task results."""
        self.db = TaskAdapter()
        self.serializer = Serializer()

    def get_task_detail(self, task_id: str) -> MergedTaskRecord:
        audit_record = self.db.find_task(task_id)
        celery_record = self.db.find_celery_result_by_id(task_id)

        task = {
            "task_id": task_id,
            "type": audit_record.get("type"),
            "payload": audit_record.get("payload"),
            "created_at": audit_record.get("created_at"),
            "status": celery_record.get("status", "QUEUED"),
            "retries": celery_record.get("result", {}).get("retries"),
            "result": celery_record.get("result"),
            "traceback": celery_record.get("traceback"),
            "runtime": celery_record.get("runtime"),
            "queue": celery_record.get("delivery_info", {}).get("routing_key", "default"),
            "worker": celery_record.get("worker"),
            "completed_at": celery_record.get("date_done")
        }
        return MergedTaskRecord.model_validate(task)


    def filter_tasks_by_type_and_date(
            self, start_date: datetime,
            end_date: datetime,
            status: TaskStatus,
        ) -> List[MergedTaskRecord]:

        """Return tasks within a date range filtered by status."""
        query = {
            "date_done": {
                "$gte": start_date,
                "$lte": end_date
            },
            "status": status.value
        }
        tasks = self.db.filter_tasks(query)
        return [MergedTaskRecord.model_validate(task) for task in tasks]



    def retry_task(self, task_id: str) -> None:
        """Retry a specific task by ID."""
        task = self.db.find_celery_result_by_id(task_id)
        if task.get('status', '').upper() != TaskStatus.FAILURE:
            raise NotFailedTaskError(task_id=task_id)

        task_name = task.get('name')
        func = TASK_MAP.get(task_name)

        if not func:
            raise ValueError(f"Task function '{task_name}' is not registered in TASK_MAP.")

        kwargs = task.get('kwargs', {})
        retry_result = func.apply_async(kwargs=kwargs)

        self.db.insert_task_audit({
            "task_id": retry_result.id,
            "retry_of": task_id,
            "name": task_name,
            "type": f"{task.get('name')}_retry",
            "payload": kwargs,
            "status": "REQUEUED",
            "created_at": datetime.now(timezone.utc)
        })

        return retry_result.id

    def retry_failed_tasks(
            self,
            start_date: datetime,
            end_date: datetime
    ) -> dict:
        """Retry failed tasks in bulk."""
        status = TaskStatus.FAILURE
        tasks = self.filter_tasks_by_type_and_date(start_date, end_date, status)
        failed_count = success_count = 0
        error_log = []

        for task in tasks:
            task_id = task["task_id"]
            try:
                self.retry_task(task_id)
                success_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Task {task_id} failed during bulk retry: {str(e)}")
                error_log.append({
                    "task_id": task_id,
                    "error": str(e)
                })

        return {
            "retried": success_count,
            "failed": failed_count,
            "total": len(tasks),
            "log": error_log
        }

    def purge_old_tasks(self, status: TaskStatus) -> str:
        """Delete tasks older than a fixed time window"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)

        result = self.db.celery_results.delete_many({
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

