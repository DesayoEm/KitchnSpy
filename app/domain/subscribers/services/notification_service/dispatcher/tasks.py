from app.infra.queues.celery_app import celery_app
from app.domain.subscribers.services.notification_service.email_config import EmailService
from app.domain.subscribers.services.notification_service.email_notifications import EmailNotificationService
from app.infra.log_service import logger

email_service = EmailService()
notification_service = EmailNotificationService()


@celery_app.task(name="send_email_notification")
def send_email_notification(notification_type, **kwargs):
    """
        Send an email notification based on the notification type.

        Args:
            notification_type (str): Type of notification to send
                - "subscription_confirmation"
                - "unsubscribed_confirmation"
                - "price_change"
                - "product_removed"
            **kwargs: Arguments required for the specific notification type

        Returns:
            bool: Success status of the email operation
        """
    try:
        if notification_type == "subscription_confirmation":
            logger.info("task called")
            return notification_service.send_subscription_confirmation(
                to_email=kwargs.get("to_email"),
                name=kwargs.get("name"),
                product_name=kwargs.get("product_name"),
                unsubscribe_link=kwargs.get("unsubscribe_link")
            )


        elif notification_type == "unsubscribed_confirmation":
            return notification_service.send_unsubscribed_confirmation(
                to_email=kwargs.get("to_email"),
                name=kwargs.get("name"),
                product_name=kwargs.get("product_name"),
                subscription_link=kwargs.get("subscription_link")
            )

        elif notification_type == "price_change":
            return notification_service.send_price_change_notification(
                to_email=kwargs.get("to_email"),
                name=kwargs.get("name"),
                product_name=kwargs.get("product_name"),
                previous_price=kwargs.get("previous_price"),
                new_price=kwargs.get("new_price"),
                price_diff=kwargs.get("price_diff"),
                change_type=kwargs.get("change_type"),
                date_checked=kwargs.get("date_checked"),
                product_link=kwargs.get("product_link")
            )

        elif notification_type == "product_removed":
            return notification_service.send_product_removed_notification(
                to_email=kwargs.get("to_email"),
                name=kwargs.get("name"),
                product_name=kwargs.get("product_name")
            )

        else:
            raise ValueError(f"Unknown notification type: {notification_type}")


    except Exception as e:
        logger.error(f"Error sending {notification_type} notification: {str(e)}")
        raise