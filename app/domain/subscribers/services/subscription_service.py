from app.domain.subscribers.services.notification_service.queued import\
    NotificationDispatcher
from app.infra.db.adapters.subscriber_adapter import SubscriberAdapter
from app.shared.exceptions import NotSubscribedError
from app.shared.serializer import Serializer
from app.domain.products.services.product_service import ProductService
from app.domain.subscribers.schemas import SubscriberData


class SubscriptionService:
    def __init__(self):
        """
        Initialize SubscriptionCrud with database access, product management, and notification services.
        """
        self.db = SubscriberAdapter()
        self.products = ProductService()
        self.notifier = NotificationDispatcher()
        self.util = Serializer()


    def serialize_document(self, document: dict | None) -> dict | None:
        """Convert ObjectId to str in a single document."""
        if document:
            return self.util.json_serialize_doc(document)


    def serialize_documents(self, documents: list[dict]) -> list[dict]:
        """Convert ObjectId to str in a list of documents."""
        if documents:
            return [self.util.json_serialize_doc(doc) for doc in documents if doc]


    def add_subscriber(self, product_id: str, data: SubscriberData) -> None:
        """Add a new subscriber to the database and send a subscription confirmation email."""
        subscriber_data = data.model_dump()

        product = self.products.find_product(product_id)

        subscriber_data["product_id"] = product_id
        subscriber_data["product_name"] = product["product_name"]
        subscriber_data["product_url"] = product["url"]

        self.db.insert_subscriber(subscriber_data)
        self.notifier.send_subscription_email(subscriber_data)


    def get_subscriber_by_email(self, value: str):
        """Yield all subscribers associated with a given product."""
        subscriber = self.db.find_subscriber_by_email(value)
        return self.serialize_documents(subscriber)


    def yield_product_subscribers(self, product_id: str):
        """Find all subscribers associated with a given product."""
        return self.db.yield_product_subscribers(product_id)


    def yield_and_paginate_product_subscribers(self, product_id: str,  page, per_page):
        """Find all subscribers associated with a given product."""
        return self.db.yield_and_paginate_product_subscribers(product_id, page, per_page)

    def yield_all_subscribers(self, page, per_page) :
        """Yield all subscribers in the database."""
        return self.db.yield_and_paginate_all_subscribers(page, per_page)


    def remove_subscriber(self, email_address: str, product_id: str) -> bool:
        """Remove a subscriber and send them an un-subscription confirmation email."""

        subscriber_data = self.db.find_product_subscriber(email_address, product_id)
        subscriber_data = self.serialize_document(subscriber_data)

        if not subscriber_data:
            raise NotSubscribedError(email_address = email_address)

        self.db.delete_subscriber(subscriber_data['_id'])
        return self.notifier.send_unsubscribed_email(subscriber_data)


    def delete_subscriber(self, subscriber_id: str) -> None:
        """Delete a subscriber by their ID"""
        self.db.delete_subscriber(subscriber_id)