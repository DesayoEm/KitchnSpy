
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.domain.subscribers.services.notification_service.tasks import send_email_notification


def test_simple_task():
    """Send a test task directly to Celery."""
    print("Sending test task...")

    task = send_email_notification.delay(
        notification_type="subscription_confirmation",
        to_email="test@example.com",
        name="Test User",
        product_name="Test Product",
        unsubscribe_link="https://example.com/unsubscribe"
    )

    print(f"Task ID: {task.id}")
    print("Waiting for task result...")


    try:
        result = task.get(timeout=10)
        print(f"Task completed with result: {result}")
    except Exception as e:
        print(f"Error getting task result: {e}")


if __name__ == "__main__":
    test_simple_task()
    print("Done! Check your worker logs for task processing information.")
