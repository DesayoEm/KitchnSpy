from app.domain.subscribers.services.notification_service.email_notifications import EmailNotificationService
from app.infra.queues.enqueue import (
    queue_subscription_confirmation,
    queue_unsubscribed_confirmation,
    queue_price_change_notification,
    queue_product_removed_notification
)
from app.infra.log_service import logger


class QueuedNotificationService(EmailNotificationService):
    """Implementation of NotificationService that queues tasks for asynchronous processing."""

    def send_subscription_confirmation(self, to_email: str, name: str, product_name: str,
                                       unsubscribe_link: str) -> bool:
        """Queue a subscription confirmation email."""
        task_id = queue_subscription_confirmation(
            to_email=to_email,
            name=name,
            product_name=product_name,
            unsubscribe_link=unsubscribe_link
        )
        logger.info(f"Queued subscription notification task: {task_id}")
        return True

    def send_unsubscribed_confirmation(self, to_email: str, name: str, product_name: str,
                                       subscription_link: str) -> bool:
        """Queue an unsubscription confirmation email."""
        task_id = queue_unsubscribed_confirmation(
            to_email=to_email,
            name=name,
            product_name=product_name,
            subscription_link=subscription_link
        )
        logger.info(f"Queued unsubscription notification task: {task_id}")
        return True

    def send_price_change_notification(self, to_email: str, name: str, product_name: str,
                                       previous_price: float, new_price: float, price_diff: float,
                                       change_type: str, date_checked: str, product_link: str) -> bool:
        """Queue a price change notification email."""
        task_id = queue_price_change_notification(
            to_email=to_email,
            name=name,
            product_name=product_name,
            previous_price=previous_price,
            new_price=new_price,
            price_diff=price_diff,
            change_type=change_type,
            date_checked=date_checked,
            product_link=product_link
        )
        logger.info(f"Queued price change notification task: {task_id}")
        return True

    def send_product_removed_notification(self, to_email: str, name: str, product_name: str) -> bool:
        """Queue a product removed notification email."""
        task_id = queue_product_removed_notification(
            to_email=to_email,
            name=name,
            product_name=product_name
        )
        logger.info(f"Queued product removed notification task: {task_id}")
        return True

