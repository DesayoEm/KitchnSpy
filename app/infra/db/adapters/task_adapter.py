from app.infra.db.adapters.shared_imports import *
from app.infra.db.adapters.base_adapter import BaseAdapter


class TaskAdapter(BaseAdapter):

    def find_task_by_id(self, task_id: str):
        return self.find_by_id(self.tasks, task_id, "Task")


    def find_failed_tasks(self, page: int = 1) -> List[dict]:
        """Retrieve failed tasks with pagination."""
        try:
            cursor = self.tasks.find({"status": "FAILURE"}).sort("date_done",pymongo.ASCENDING)
            failed_tasks = self.paginate_results(cursor, page, 10)

            if not failed_tasks:
                raise DocsNotFoundError(entities="failed tasks", page=page)
            return failed_tasks

        except Exception as e:
            if not isinstance(e, DocsNotFoundError):
                logger.error(f"Error retrieving failed tasks: {str(e)}")
                raise


    def find_recent_tasks(self, page:int = 1)-> List[dict]:
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
