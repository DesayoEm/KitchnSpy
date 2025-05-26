
from app.infra.queues.enqueue import queue_product_removed_notification


class NotificationDispatcher:
    @staticmethod
    def send_product_removed_notification(deleted_product_data: dict):
        return queue_product_removed_notification(
            to_email=deleted_product_data["to_email"],
            name=deleted_product_data["name"],
            product_name=deleted_product_data["product_name"]
        )