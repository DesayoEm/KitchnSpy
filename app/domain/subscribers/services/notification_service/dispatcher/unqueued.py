from app.domain.subscribers.services.notification_service.email_notifications import EmailNotificationService

class UnqueuedNotificationDispatcher:
    def __init__(self):
        self.service = EmailNotificationService()

    def send_subscription_email(self, subscriber_data: dict):
        return self.service.send_subscription_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            unsubscribe_link=f"https://kitchnspy.com/subscriptions/{subscriber_data['product_id']}/unsubscribe?email={subscriber_data['email_address']}"
        )

    def send_unsubscribed_email(self, subscriber_data: dict):
        return self.service.send_unsubscribed_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            subscription_link=f"https://kitchnspy.com/product/subscribe?email={subscriber_data['email_address']}"
        )
