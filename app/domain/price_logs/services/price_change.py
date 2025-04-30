from app.domain.subscribers.services.notification_service import NotificationService
from app.domain.products.services.product_service import ProductService
from app.domain.subscribers.services.subscription_service import SubscriptionService
from app.infra.log_service import logger


class PriceChangeService:
    def __init__(self):
        self.subscribers = SubscriptionService()
        self.notification = NotificationService()
        self.products = ProductService()

    @staticmethod
    def detect_change(previous_price: float, new_price: float):
        if new_price > previous_price:
            price_diff = new_price-previous_price
            change_type = "Rise"
            trigger = True
        elif previous_price > new_price:
            price_diff = previous_price - new_price
            change_type = "Drop"
            trigger = True
        else:
            price_diff = 0.0
            change_type = "No change"
            trigger = False

        return {
            "trigger": trigger,
            "price_diff": price_diff,
            "change_type": change_type
        }

    def notify_subscribers(
        self, product_id: str, previous_price: float, new_price: float, price_diff: float,
        change_type: str, date_checked: str
            ):
        subscribers = list(self.subscribers.yield_product_subscribers(product_id))
        logger.info(f"Found {len(subscribers)} subscribers for product {product_id}")
        product = self.products.find_product(product_id)

        for subscriber in subscribers:
            logger.info(f"Found {len(subscribers)} subscribers for product {product_id}")

            self.notification.send_price_change_notification(
                 subscriber['email_address'],  subscriber['name'], product['product_name'],
                previous_price, new_price, price_diff, change_type, date_checked, product['url']
                )



