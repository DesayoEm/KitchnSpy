from app.core.database.mongo_gateway import MongoGateway
from app.core.exceptions import NotSubscribedError
from app.core.services.notifications.notifications import NotificationService
from app.core.utils import Utils
from app.crud.products import ProductCrud
from app.core.database.validation.subscription import SubscriberData


class SubscriptionCrud:
    def __init__(self):
        """
        Initialize SubscriberCrud with database access, product management, and notification services.
        """
        self.db = MongoGateway()
        self.products = ProductCrud()
        self.notifier = NotificationService()
        self.util = Utils()

    def serialize_document(self, document: dict | None) -> dict | None:
        """Convert ObjectId to str in a single document."""
        return self.util.convert_objectid_to_str(document)


    def serialize_documents(self, documents: list[dict]) -> list[dict]:
        """Convert ObjectId to str in a list of documents."""
        return [self.util.convert_objectid_to_str(doc) for doc in documents if doc]


    def add_subscriber(self, product_id: str, data: SubscriberData) -> None:
        """Add a new subscriber to the database and send a subscription confirmation email."""
        subscriber_info = data.model_dump()

        product = self.products.find_product(product_id)

        subscriber_info["product_id"] = product_id
        subscriber_info["product_name"] = product["product_name"]
        subscriber_info["product_url"] = product["url"]

        self.db.insert_subscriber(subscriber_info)
        self.send_subscription_email(subscriber_info)


    def send_subscription_email(self, subscriber_data: dict) -> None:
        """Send a subscription confirmation email to a new subscriber."""
        unsubscribe_link = f"https://kitchnspy.com/subscriptions/{subscriber_data['product_id']}/unsubscribe?email={subscriber_data['email_address']}"

        self.notifier.send_subscription_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            unsubscribe_link=unsubscribe_link
        )


    def find_all_subscribers(self, product_id: str) -> list[dict]:
        """Find all subscribers associated with a given product."""
        subscribers = list(self.db.find_subscribers(product_id))
        return self.serialize_documents(subscribers)


    def yield_product_subscribers(self, product_id: str) -> list[dict]:
        """Find all subscribers associated with a given product."""
        return self.db.yield_product_subscribers(product_id)


    def remove_subscriber(self, product_id: str, email_address: str) -> bool:
        """Remove a subscriber and send them an un-subscription confirmation email."""
        subscriber_data = self.db.find_subscriber(product_id, email_address)
        if not subscriber_data:
            raise NotSubscribedError(email_address = email_address)

        subscription_link = f"https://kitchnspy.com/product/subscribe?email={subscriber_data['email_address']}"

        self.db.delete_subscriber(subscriber_data['email_address'])
        return self.notifier.send_unsubscribed_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            subscription_link=subscription_link
        )

    def delete_subscriber(self, subscriber_id: str) -> None:
        """
        Delete a subscriber by their ID.
        Args:
            subscriber_id (str): The MongoDB ObjectId of the subscriber.
        """
        self.db.delete_subscriber(subscriber_id)