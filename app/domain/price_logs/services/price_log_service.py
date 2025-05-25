from datetime import datetime, timezone, timedelta
from bson import ObjectId

from app.domain.price_logs.services.notification_service.queued import NotificationDispatcher
from app.infra.db.adapters.price_log_adapter import PriceLogAdapter
from app.shared.exceptions import URLNotFoundError
from app.infra.scraping.kitchenaid_scraper import Scraper
from app.domain.products.services.product_service import ProductService
from app.domain.price_logs.utils import PriceUtils
from typing import Iterator
from app.infra.log_service import logger
from app.shared.serializer import Serializer


class PriceLogService:
    def __init__(self):
        """
        Initialize PriceLogService with database access, product CRUD operations, and scraper service.
        """
        self.db = PriceLogAdapter()
        self.products = ProductService()
        self.scraper = Scraper()
        self.util = PriceUtils()
        self.serializer = Serializer()
        self.notifier = NotificationDispatcher()



    def log_price(self, product_id: str) -> dict:
        """Log the current price of a product by scraping it and comparing it to the existing stored price."""
        existing = self.products.find_product(product_id)
        new= self.scraper.scrape_product({
                    "name": existing["name"],
                    "url": existing["url"]
                })
        if not new:
            raise URLNotFoundError(url=existing['url'])

        try:
            previous_price = self.util.parse_price(existing["price"])
            cleaned_new_price = self.util.validate_price_format(new["price"])
            new_price  = self.util.parse_price(cleaned_new_price)

            change = self.util.detect_change(previous_price, new_price)

            data = {
                "product_id": str(ObjectId(product_id)),
                "previous_price": existing["price"],
                "current_price": cleaned_new_price,
                "price_diff": change["price_diff"],
                "change_type": change["change_type"],
                "date_checked": datetime.now(timezone.utc)
            }

            self.db.insert_price_log(data)

            if not change["trigger"]:#event
                date_str = data["date_checked"].strftime('%Y-%m-%d')
                self.notify_subscribers(
                    product_id, previous_price, new_price, change["price_diff"], change["change_type"],
                    date_str
                )

            return self.serializer.json_serialize_doc(data)

        except Exception:
            raise

    def notify_subscribers(
        self, product_id: str, previous_price: float, new_price: float, price_diff: float,
        change_type: str, date_checked: str
            ):

        from app.domain.subscribers.services.subscription_service import SubscriptionService
        subscribers = SubscriptionService()

        subscribers = list(subscribers.yield_product_subscribers(product_id))
        logger.info(f"Found {len(subscribers)} subscribers for product {product_id}")
        product = self.products.find_product(product_id)

        for subscriber in subscribers:
            logger.info(f"Found {len(subscribers)} subscribers for product {product_id}")

            price_change_data = {
                "to_email": subscriber['email_address'], "name": subscriber['name'],
                "product_name": product['product_name'], "previous_price": previous_price,
                "new_price": new_price, "price_diff": price_diff, "change_type": change_type,
                "date_checked": date_checked, "product_link": product['url']
            }

            self.notifier.send_price_change_notification(price_change_data)


    def log_prices(self) -> dict:
        """Log prices for all products and return a summary."""
        updated_count = 0
        error_count = 0

        product_ids = self.products.compile_product_ids()

        for product_id in product_ids:
            try:
                self.log_price(product_id)
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to log price for product {product_id}: {str(e)}")
                error_count += 1

        return {
            "total_products": len(product_ids),
            "updated": updated_count,
            "errors": error_count
        }


    def yield_product_price_history(self, product_id: str) -> Iterator[dict]:
        """Yield the price history for a specific product one by one."""
        return self.db.yield_product_price_history(product_id)

    def yield_and_paginate_product_price_history(self, product_id: str, page: int, per_page: int) -> Iterator[dict]:
        """Yield the price history for a specific product one by one."""
        return self.db.yield_and_paginate_product_price_history(product_id, page, per_page)

    def yield_and_paginate_all_prices(self, page: int, per_page: int) -> Iterator[dict]:
        """Yield all price logs across all products."""
        return self.db.yield_and_paginate_all_price_logs(page, per_page)

    def delete_price(self, price_id: str) -> None:
        """Delete a price log entry by its ID."""
        self.db.delete_price(price_id)

    def delete_old_price_logs(self) -> str:
        """Delete all price log entries older than 1 year ago."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(minutes=1)
        # cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)

        result = self.db.price_logs.delete_many({
            "date_checked": {"$lt": cutoff_date}
        })
        deleted_count = result.deleted_count
        logger.info(f"{deleted_count} price logs deleted")
        return f"Deleted {deleted_count} prices"



