from app.domain.subscribers.services.notification_service.dispatcher.tasks import send_email_notification
from app.infra.log_service import logger


def queue_subscription_confirmation(to_email, name, product_name, unsubscribe_link):
    """
    Queue a subscription confirmation email.

    Args:
        to_email (str): Recipient's email address
        name (str): Recipient's name
        product_name (str): Name of the product subscribed to
        unsubscribe_link (str): Link for unsubscribing

    Returns:
        str: Task ID of the queued task
    """
    task = send_email_notification.delay(
        notification_type="subscription_confirmation",
        to_email=to_email,
        name=name,
        product_name=product_name,
        unsubscribe_link=unsubscribe_link
    )
    logger.info("Enqueue called")

    return task.id


def queue_unsubscribed_confirmation(to_email, name, product_name, subscription_link):
    """
    Queue an unsubscription confirmation email.

    Args:
        to_email (str): Recipient's email address
        name (str): Recipient's name
        product_name (str): Name of the product unsubscribed from
        subscription_link (str): Link to resubscribe

    Returns:
        str: Task ID of the queued task
    """
    task = send_email_notification.delay(
        notification_type="unsubscribed_confirmation",
        to_email=to_email,
        name=name,
        product_name=product_name,
        subscription_link=subscription_link
    )
    return task.id


def queue_price_change_notification(to_email, name, product_name, previous_price,
                                    new_price, price_diff, change_type, date_checked, product_link):
    """
    Queue a price change notification email.

    Args:
        to_email (str): Recipient's email address
        name (str): Recipient's name
        product_name (str): Name of the product with price change
        previous_price (float): Previous price
        new_price (float): New price
        price_diff (float): Price difference
        change_type (str): Type of change ('drop' or 'increase')
        date_checked (str): Date when the price was checked
        product_link (str): Link to the product

    Returns:
        str: Task ID of the queued task
    """
    task = send_email_notification.delay(
        notification_type="price_change",
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
    return task.id


def queue_product_removed_notification(to_email, name, product_name):
    """
    Queue a product removed notification email.

    Args:
        to_email (str): Recipient's email address
        name (str): Recipient's name
        product_name (str): Name of the removed product

    Returns:
        str: Task ID of the queued task
    """
    task = send_email_notification.delay(
        notification_type="product_removed",
        to_email=to_email,
        name=name,
        product_name=product_name
    )
    return task.id