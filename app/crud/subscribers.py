from app.core.database.mongo_gateway import MongoGateway
from app.core.services.notifications.notifications import NotificationService
from app.crud.scrape import ScraperCrud


class SubscriptionCrud:
    def __init__(self):
        self.db = MongoGateway()
        self.scraper = ScraperCrud()
        self.notifier = NotificationService()


    def add_subscriber(self, data: dict):
        self.db.insert_subscriber(data)
        self.send_subscription_email(data)

    def remove_subscriber(self, subscriber_data: dict):
        subscription_link = f"https://kitchnspy.com/product/subscribe?email={subscriber_data['email_address']}"

        self.db.delete_subscriber(subscriber_data['email_address'])
        return self.notifier.send_unsubscribed_confirmation(
            to_email=subscriber_data["email_address"],
            name=subscriber_data["name"],
            product_name=subscriber_data["product_name"],
            subscription_link=subscription_link
        )



    def send_subscription_email(self, subscriber_data: dict):
        name = subscriber_data.get("name", "there")
        product_name = subscriber_data.get("product_name", "a product")

        unsubscribe_link = f"https://kitchnspy.com/unsubscribe?email={subscriber_data['email_address']}"

        return self.notifier.send_subscription_confirmation(
            to_email=subscriber_data["email_address"],
            name=name,
            product_name=product_name,
            unsubscribe_link=unsubscribe_link
        )

