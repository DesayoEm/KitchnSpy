from app.infra.db.adapters.shared_imports import *
from app.infra.db.adapters.base_adapter import BaseAdapter


class TaskAdapter(BaseAdapter):

    def insert_task_audit(self, data: dict):
        self.tasks.insert_one(data)

    def find_task_by_id(self, _id: str):
        return self.find_by_id(self.tasks, _id, "Task")

    def find_task(self, task_id: str):
        task = self.tasks.find({"task_id": task_id})
        if not task:
            raise DocNotFoundError(identifier=task_id, entity="task")

    def find_celery_result_by_id(self, task_id: str):
        result = self.celery_results.find({"_id": task_id})
        return result


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


    def filter_tasks(self, query, per_page, page:int = 1)-> List[dict]:
        try:
            cursor = self.tasks.find(query).sort("date_done", pymongo.ASCENDING)
            recent_tasks = self.paginate_results(cursor, per_page, page)

            if not recent_tasks:
                raise DocsNotFoundError(entities="tasks", page=page)
            return recent_tasks

        except Exception as e:
            if not isinstance(e, DocsNotFoundError):
                logger.error(f"Error retrieving recent tasks: {str(e)}")
                raise

    
    def delete_task(self, task_id: str) -> None:
        """ Delete a task document from the database by its ID."""
        obj_id = self.validate_obj_id(task_id, "Task")

        try:
            result = self.tasks.delete_one({"_id": obj_id})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Deleted task {task_id}")
            else:
                raise DocNotFoundError(identifier=task_id, entity="Task")

        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise
