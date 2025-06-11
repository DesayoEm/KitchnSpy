from datetime import datetime, timezone, timedelta, date
from typing import List

from app.domain.price_logs.services.notification_service.tasks import send_price_email_notification
from app.domain.products.services.notification_service.tasks import send_product_email_notification
from app.domain.subscribers.services.notification_service.tasks import send_subscription_email_notification

from app.infra.db.adapters.task_adapter import TaskAdapter
from app.infra.log_service import logger
from app.infra.services.monitoring.schemas import TaskStatus, MergedTaskRecord
from app.shared.exceptions import NotFailedTaskError, DocNotFoundError
from app.shared.serializer import Serializer

now = datetime.now(timezone.utc)


TASK_MAP = {
    "send_product_email_notification": send_product_email_notification,
    "send_price_email_notification": send_price_email_notification,
    "send_subscription_email_notification": send_subscription_email_notification,

}
class TaskMonitoringService:
    def __init__(self):
        """Service for monitoring and managing Celery task results."""
        self.db = TaskAdapter()
        self.serializer = Serializer()

    def get_task_detail(self, task_id: str) -> MergedTaskRecord:
        audit_record = self.db.find_task(task_id)
        celery_record = self.db.find_celery_result_by_id(task_id)

        if not audit_record:
            raise DocNotFoundError(identifier=task_id, entity="task")

        logger.info(audit_record)

        task = {
            "task_id": task_id,
            "name": audit_record.get("name"),
            "payload": audit_record.get("payload"),
            "created_at": audit_record.get("created_at"),
            "status": celery_record.get("status", "QUEUED"),
            "retries": celery_record.get("retries"),
            "result": celery_record.get("result"),
            "traceback": celery_record.get("traceback"),
            "runtime": celery_record.get("runtime"),
            "queue": celery_record.get("delivery_info", {}).get("routing_key", "default"),
            "worker": celery_record.get("worker"),
            "completed_at": celery_record.get("date_done")
        }
        return MergedTaskRecord.model_validate(task)


    def filter_tasks_by_type_and_date(
            self,
            start_date: date,
            end_date: date,
            status: TaskStatus,
    ) -> List[MergedTaskRecord]:
        """Return tasks within a date range filtered by status."""

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

        celery_query = {"status": status.value}

        if status.value in ["SUCCESS", "FAILURE", "REVOKED"]:
            celery_query["date_done"] = {"$gte": start_dt, "$lt": end_dt}

        celery_tasks = list(self.db.find_celery_tasks(celery_query))

        merged_tasks = []
        for celery_task in celery_tasks:
            task_id = celery_task.get("_id")
            audit_record = self.db.find_task(task_id)

            task_data = {
                "task_id": task_id,
                "name": audit_record.get("name"),
                "payload": audit_record.get("payload"),
                "created_at": audit_record.get("created_at"),
                "status": celery_task.get("status", "QUEUED"),
                "retries": celery_task.get("retries"),
                "result": celery_task.get("result"),
                "traceback": celery_task.get("traceback"),
                "runtime": celery_task.get("runtime"),
                "queue": celery_task.get("delivery_info", {}).get("routing_key", "default"),
                "worker": celery_task.get("worker"),
                "completed_at": celery_task.get("date_done", None),
            }

            try:
                merged_tasks.append(MergedTaskRecord.model_validate(task_data))
            except Exception as e:
                logger.error(f"Failed to validate task {task_id}: {e}")
                logger.debug(f"Task data: {task_data}")
                continue

        return merged_tasks


    def retry_failed_task(self, task_id: str) -> None:
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
            "created_at": now,
            "created_at_date": datetime.combine(now.date(), datetime.min.time())
        })

        return retry_result.id


    def retry_failed_tasks(
            self,
            start_date: date,
            end_date: date
    ) -> dict:
        """Retry failed tasks in bulk."""
        status = TaskStatus.FAILURE
        tasks = self.filter_tasks_by_type_and_date(start_date, end_date, status)
        failed_count = success_count = 0
        error_log = []

        for task in tasks:
            task_id = task["task_id"]
            try:
                self.retry_failed_task(task_id)
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


    def count_tasks(self) -> str:
        """Count all tasks in the collection."""
        result = self.db.tasks.count_documents({})
        return f"{result} tasks found"


    def count_filtered_tasks(self, start_date: date, end_date: date, status: TaskStatus) -> str:
        """Count tasks within a date range filtered by status."""

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

        if status.value != "QUEUED":
            query = {
                "date_done": {
                    "$gte": start_dt,
                    "$lt": end_dt
                },
                "status": status.value
            }
            result = self.db.celery_results.count_documents(query)

        else:
            query = {
                "created_at_date": {
                    "$gte": start_dt,
                    "$lt": end_dt
                }
            }

            audit_tasks = self.db.filter_tasks(query)
            count = 0

            for task in audit_tasks:
                task_id = task.get("task_id")
                if task_id and not self.db.find_celery_result_by_id(task_id):
                    count += 1

            result = count

        return f"{result} {status.value} tasks found"


    def delete_task(self, task_id: str) -> str:
        """ Delete a task document from both the task_audit and celery collections by its ID."""
        try:
            self.db.delete_task_audit(task_id)
            self.db.delete_celery_result(task_id)
            return "Task deleted"

        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise


    def purge_old_tasks(self, status: TaskStatus) -> None:
        """Delete tasks older than a fixed time window"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)

        audit_query = {
            "created_at_date": {"$lt": cutoff_date},
            "status": status.value
            }
        tasks = self.db.filter_tasks(audit_query)
        for task in tasks:
            self.db.delete_task_audit(task["task_id"])


        celery_query = {
             "date_done": {"$lt": cutoff_date},
             "status": status.value
            }
        celery_tasks = self.db.filter_celery_tasks(celery_query)
        if celery_tasks:
            for celery_task in celery_tasks:
                self.db.delete_celery_result(celery_task["_id"])

        logger.info(f"{status.value} Tasks purged older than {cutoff_date} purged")
