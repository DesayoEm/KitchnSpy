from app.infra.db.adapters.shared_imports import *
from app.infra.db.adapters.base_adapter import BaseAdapter
from uuid import UUID


class TaskAdapter(BaseAdapter):

    def insert_task_audit(self, data: dict):
        self.tasks.insert_one(data)

    def find_task_by_id(self, _id: str):
        return self.find_by_id(self.tasks, _id, "Task")

    def find_tasks_by_status(self, status: str):
        tasks = self.tasks.find({"status": status})
        return tasks

    def find_task(self, task_id: str):
        logger.debug(f"Looking up task by ID: {task_id} (type: {type(task_id)})")
        task = self.tasks.find_one({"task_id": task_id.strip()})  # no UUID conversion
        if not task:
            raise DocNotFoundError(identifier=task_id, entity="task")
        return task


    def find_celery_result_by_id(self, task_id: str):
        result = self.celery_results.find_one({"_id": task_id})
        return result

    def find_celery_tasks(self, query) -> List:
        celery_tasks = self.celery_results.find(query)
        return celery_tasks

    def filter_tasks(self, query) -> List[dict]:
        return self.tasks.find(query)

    def filter_celery_tasks(self, query) -> List[dict]:
        return self.celery_results.find(query)


    def find_all_tasks(self, page: int = 1) -> List[dict]:
        try:
            cursor = self.tasks.find({}).sort("date_done", pymongo.ASCENDING)
            recent_tasks = self.paginate_results(cursor, page, 10)

            if not recent_tasks:
                raise DocsNotFoundError(entities="recent tasks", page=page)
            return recent_tasks

        except Exception as e:
            if not isinstance(e, DocsNotFoundError):
                logger.error(f"Error retrieving recent tasks: {str(e)}")
                raise


    
    def delete_task_audit(self, task_id: str) -> None:
        """ Delete a task document from the database by its ID."""
        self.tasks.delete_one({"task_id": task_id})


    def delete_celery_result(self, task_id: str) -> None:
        """ Delete a task document from the database by its ID."""
        self.celery_results.delete_one({"_id": task_id})


