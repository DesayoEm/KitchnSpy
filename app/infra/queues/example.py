"""
Example usage of the email enqueuing system.
This shows how to use the enqueue functions in your application.
"""

from app.infra.queues.enqueue import (
    queue_subscription_confirmation,
)


def example_subscription_confirmation():
    """Example of sending a subscription confirmation email."""
    task_id = queue_subscription_confirmation(
        to_email="user@example.com",
        name="John Doe",
        product_name="Kitchen Mixer XYZ",
        unsubscribe_link="https://kitchnspy.com/unsubscribe/abc123"
    )
    print(f"Queued subscription confirmation email: {task_id}")



if __name__ == "__main__":
    example_subscription_confirmation()

    print("Email task has been queued. Make sure the Celery worker is running to process it.")
    print("You can start the worker with: 'windows_celery_worker.bat' on Windows")