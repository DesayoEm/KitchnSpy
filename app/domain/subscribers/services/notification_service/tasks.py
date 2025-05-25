from app.infra.queues.celery_app import celery_app
from app.infra.services.notifications.email_templates import EmailTemplateService
from app.infra.log_service import logger

template = EmailTemplateService()


@celery_app.task(name="send_email_notification")
def send_email_notification(notification_type, **kwargs):
    """
        Send an email notification based on the notification type.

        Args:
            notification_type (str): Type of notification to send
                - "subscription_confirmation"
                - "unsubscribed_confirmation"
            **kwargs: Arguments required for the specific notification type

        Returns:
            bool: Success status of the email operation
        """
    try:
        if notification_type == "subscription_confirmation":
            logger.info("task called")
            return template.send_subscription_confirmation(
                to_email=kwargs.get("to_email"),
                name=kwargs.get("name"),
                product_name=kwargs.get("product_name"),
                unsubscribe_link=kwargs.get("unsubscribe_link")
            )


        elif notification_type == "unsubscribed_confirmation":
            return template.send_unsubscribed_confirmation(
                to_email=kwargs.get("to_email"),
                name=kwargs.get("name"),
                product_name=kwargs.get("product_name"),
                subscription_link=kwargs.get("subscription_link")
            )

        else:
            raise ValueError(f"Unknown notification type: {notification_type}")


    except Exception as e:
        logger.error(f"Error sending {notification_type} notification: {str(e)}")
        raise