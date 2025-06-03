from app.infra.queues.celery_app import celery_app
from app.infra.services.notifications.email_templates import EmailTemplateService
import smtplib
from app.infra.log_service import logger

template = EmailTemplateService()


@celery_app.task(name="send_subscription_email_notification",
                 bind = True,
                autoretry_for=(smtplib.SMTPException, ConnectionError),
                retry_kwargs={"max_retries": 2},
                 default_retry_delay=60)
def send_subscription_email_notification(self, notification_type, **kwargs):
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

    except (smtplib.SMTPException, ConnectionError) as exc:
        logger.error(f"Error sending {notification_type} notification: {str(exc)}")
        raise self.retry(exc=exc)

    except Exception as exc:
        logger.error(f"Error sending {notification_type} notification: {str(exc)}")
        raise
