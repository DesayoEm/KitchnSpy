from app.infra.queues.enqueue import (
    queue_subscription_confirmation,
    queue_unsubscribed_confirmation,
)

class NotificationDispatcher:
    def send_subscription_email(self, subscriber_data: dict):
        return queue_subscription_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            unsubscribe_link=f"https://kitchnspy.com/subscriptions/{subscriber_data['product_id']}/unsubscribe?email={subscriber_data['email_address']}"
        )

    def send_unsubscribed_email(self, subscriber_data: dict):
        return queue_unsubscribed_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            subscription_link=f"https://kitchnspy.com/product/subscribe?email={subscriber_data['email_address']}"
        )