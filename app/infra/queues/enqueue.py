from app.domain.price_logs.services.notification_service import tasks as price_tasks
from app.domain.products.services.notification_service import tasks as product_tasks
from app.domain.subscribers.services.notification_service import tasks as subscriber_tasks
from app.infra.db.adapters.task_adapter import TaskAdapter
from datetime import datetime, UTC
from app.infra.log_service import logger

db = TaskAdapter()

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
    task = subscriber_tasks.send_subscription_email_notification.apply_async(
        kwargs={
            "notification_type": "subscription_confirmation",
            "to_email": to_email,
            "name": name,
            "product_name": product_name,
            "unsubscribe_link": unsubscribe_link
        }
    )
    db.insert_task_audit({
        "task_id": task.id,
        "name": "subscription_confirmation",
        "payload": {
            "to_email": to_email,
            "name": name,
            "product_name": product_name,
            "unsubscribe_link": unsubscribe_link
        },
        "status": "QUEUED",
        "created_at": datetime.now(UTC)
    })

    logger.info("Enqueue + audit log recorded")
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
    task = subscriber_tasks.send_subscription_email_notification.apply_async(
        kwargs= {
        "notification_type":"unsubscribed_confirmation",
        "to_email":to_email,
        "name":name,
        "product_name":product_name,
        "subscription_link":subscription_link
    }
    )
    db.insert_task_audit({
        "task_id": task.id,
        "name": "unsubscribed_confirmation",
        "payload": {
            "to_email": to_email,
            "name": name,
            "product_name": product_name,
            "subscription_link": subscription_link
        },
        "status": "QUEUED",
        "created_at": datetime.now(UTC)
    })

    logger.info("Enqueue + audit log recorded")
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
    task = price_tasks.send_price_email_notification.apply_async(
        kwargs = {
            "notification_type": "price_change",
            "to_email": to_email,
            "name": name,
            "product_name": product_name,
            "previous_price": previous_price,
            "new_price": new_price,
            "price_diff": price_diff,
            "change_type": change_type,
            "date_checked": date_checked,
            "product_link":product_link
        }
    )
    db.insert_task_audit({
        "task_id": task.id,
        "name": "price_change",
        "payload": {
            "to_email": to_email,
            "name": name,
            "product_name": product_name,
            "previous_price": previous_price,
            "new_price": new_price,
            "price_diff": price_diff,
            "change_type": change_type,
            "date_checked": date_checked,
            "product_link":product_link
        },
        "status": "QUEUED",
        "created_at": datetime.now(UTC)
    })

    logger.info("Enqueue + audit log recorded")
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
    task = product_tasks.send_product_email_notification.apply_async(
        kwargs = {
            "notification_type": "product_removed",
            "to_email": to_email,
            "name": name,
            "product_name": product_name
        }

    )
    db.insert_task_audit({
        "task_id": task.id,
        "name": "product_removed",
        "payload": {
            "to_email": to_email,
            "name": name,
            "product_name": product_name
        },
        "status": "QUEUED",
        "created_at": datetime.now(UTC)
    })

    logger.info("Enqueue + audit log recorded")
    return task.id

