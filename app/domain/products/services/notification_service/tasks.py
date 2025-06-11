from app.infra.queues.celery_app import celery_app
import smtplib
from app.infra.services.notifications.email_templates import EmailTemplateService
from app.infra.log_service import logger

template = EmailTemplateService()


@celery_app.task(name="send_product_email_notification",
                 bind=True,
                 autoretry_for=(smtplib.SMTPException, ConnectionError),
                 retry_kwargs={"max_retries": 2},
                 default_retry_delay=60)

def send_product_email_notification(self, notification_type, **kwargs):
    """
        Send an email notification based on the notification type.
        Args:
            notification_type (str): Type of notification to send
                - "product_removed"
            **kwargs: Arguments required for the specific notification type
        Returns:
            bool: Success status of the email operation
        """
    try:
        if notification_type == "product_removed":
            return template.send_product_removed_notification(
                to_email=kwargs.get("to_email"),
                name=kwargs.get("name"),
                product_name=kwargs.get("product_name")
            )

        else:
            raise ValueError(f"Unknown notification type: {notification_type}")

    except (smtplib.SMTPException, ConnectionError) as exc:
        logger.error(f"Error sending {notification_type} notification: {str(exc)}")
        raise self.retry(exc=exc)

    except Exception as exc:
        logger.error(f"Error sending {notification_type} notification: {str(exc)}")
        raise