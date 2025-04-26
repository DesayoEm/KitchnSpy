from app.core.database.mongo_gateway import MongoGateway
from app.core.services.notifications.notifications import NotificationService
from app.crud.products import ProductCrud


class SubscriptionCrud:
    def __init__(self):
        """
        Initialize the SubscriptionCrud with database access, product management, and notification services.
        """
        self.db = MongoGateway()
        self.scraper = ProductCrud()
        self.notifier = NotificationService()

    def add_subscriber(self, data: dict) -> None:
        """
        Add a new subscriber to the database and send them a subscription confirmation email.
        Args:
            data (dict): A dictionary containing subscriber information.
        """
        self.db.insert_subscriber(data)
        self.send_subscription_email(data)


    def remove_subscriber(self, subscriber_data: dict) -> bool:
        """
        Remove a subscriber from the database and send them an unsubscription confirmation email.
        Args:
            subscriber_data (dict): A dictionary containing the subscriber's details

        Returns:
            dict: The result of the unsubscription notification sending operation.
        """

        subscription_link = f"https://kitchnspy.com/product/subscribe?email={subscriber_data['email_address']}"

        self.db.delete_subscriber(subscriber_data['email_address'])
        return self.notifier.send_unsubscribed_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            subscription_link=subscription_link
        )


    def send_subscription_email(self, subscriber_data: dict) -> bool:
        """
        Send a subscription confirmation email to a new subscriber.
        Args:
            subscriber_data (dict): A dictionary containing the subscriber's details.

        Returns:
            dict: The result of the subscription confirmation notification sending operation.
        """
        name = subscriber_data.get("name", "there")
        product_name = subscriber_data.get("product_name", "a product")

        unsubscribe_link = f"https://kitchnspy.com/unsubscribe?email={subscriber_data['email_address']}"

        return self.notifier.send_subscription_confirmation(
            to_email=subscriber_data["email_address"],
            name=name,
            product_name=product_name,
            unsubscribe_link=unsubscribe_link
        )
