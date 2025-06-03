from app.infra.queues.celery_app import celery_app
import smtplib
from app.infra.services.notifications.email_templates import EmailTemplateService
from celery import Task
from app.infra.log_service import logger

template = EmailTemplateService()


@celery_app.task(name="send_price_email_notification",
                 bind=True,
                 autoretry_for=(smtplib.SMTPException, ConnectionError),
                 retry_kwargs={"max_retries": 2},
                 default_retry_delay=60)

def send_price_email_notification(self, notification_type, **kwargs):
    """
        Send an email notification based on the notification type.
        Args:
            notification_type (str): Type of notification to send
                - "price_change"
            **kwargs: Arguments required for the specific notification type

        Returns:
            bool: Success status of the email operation
        """
    try:
        if notification_type == "price_change":
            return template.send_price_change_notification(
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

        else:
            raise ValueError(f"Unknown notification type: {notification_type}")


    except (smtplib.SMTPException, ConnectionError) as exc:
        logger.error(f"Error sending {notification_type} notification: {str(exc)}")
        raise self.retry(exc=exc)

    except Exception as exc:
        logger.error(f"Error sending {notification_type} notification: {str(exc)}")
        raise