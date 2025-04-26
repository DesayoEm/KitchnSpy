from app.core.database.mongo_gateway import MongoGateway
from app.core.services.notifications.notifications import NotificationService
from app.crud.products import ProductCrud
from app.core.utils import Utils


class SubscriptionCrud:
    def __init__(self):
        """
        Initialize SubscriptionCrud with database access, product management, and notification services.
        """
        self.db = MongoGateway()
        self.products = ProductCrud()
        self.notifier = NotificationService()
        self.util = Utils()

    def add_subscriber(self, data: dict) -> None:
        """
        Add a new subscriber to the database and send them a subscription confirmation email.
        Args:
            data (dict): A dictionary containing subscriber information (email_address, name, product_name).
        """
        self.db.insert_subscriber(data)
        self.send_subscription_email(data)


    def find_all_subscribers(self, product_id: str) -> list[dict]:
        """
        Find all subscribers associated with a given product.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Returns:
            list[dict]: A list of subscriber documents.
        """
        subscribers = list(self.db.find_subscribers(product_id))
        return [
            self.util.convert_objectid_to_str(subscriber) for subscriber in subscribers
        ]



    def delete_subscriber(self, subscriber_id: str) -> None:
        """
        Delete a subscriber by their ID.
        Args:
            subscriber_id (str): The MongoDB ObjectId of the subscriber.
        """
        self.db.delete_subscriber(subscriber_id)


    def remove_subscriber(self, subscriber_data: dict) -> bool:
        """
        Remove a subscriber and send them an unsubscription confirmation email.
        Args:
            subscriber_data (dict): A dictionary containing subscriber details (name, email_address, product_name).

        Returns:
            bool: Whether the unsubscription confirmation email was sent successfully.
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
            subscriber_data (dict): A dictionary containing subscriber details (name, email_address, product_name).

        Returns:
            bool: Whether the subscription confirmation email was sent successfully.
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
