from datetime import datetime, timezone
from bson import ObjectId
from app.core.database.mongo_gateway import MongoGateway
from app.core.exceptions import PriceLoggingError, URLNotFoundError
from app.core.services.price_change import PriceChangeService
from app.core.services.scraper import Scraper
from app.crud.products import ProductCrud
from app.core.utils import Utils
from typing import Iterator


class PricesCrud:
    def __init__(self):
        """
        Initialize the PricesCrud with database access, product CRUD operations, and scraper service.
        """
        self.db = MongoGateway()
        self.products = ProductCrud()
        self.scraper = Scraper()
        self.util = Utils()
        self.price_service = PriceChangeService


    def serialize_document(self, document: dict | None) -> dict | None:
        """Convert ObjectId to str in a single document."""
        return self.util.convert_objectid_to_str(document)


    def serialize_documents(self, documents: list[dict]) -> list[dict]:
        """Convert ObjectId to str in a list of documents."""
        return [self.util.convert_objectid_to_str(doc) for doc in documents if doc]


    def log_price(self, product_id: str) -> dict:
        """Log the current price of a product by scraping it and comparing it to the existing stored price."""
        existing = self.db.find_product(product_id)
        current = self.scraper.scrape_product(existing['url'])

        if not current:
            raise URLNotFoundError(url=existing['url'])

        try:
            previous_price = self.util.parse_price(existing["price"])
            new_price  = self.util.parse_price(current["price"])

            change = self.price_service.detect_change(previous_price, new_price)

            data = {
                "product_id": ObjectId(product_id),
                "previous_price": existing["price"],
                "current_price": current["price"],
                "price_diff": change["price_diff"],
                "change_type": change["change_type"],
                "date_checked": datetime.now(timezone.utc)
            }
            self.db.insert_price_log(data)
            if change["trigger"]:
                date_str = data["date_checked"].strftime('%Y-%m-%d')
                self.price_service.notify_subscribers(
                    product_id, previous_price, new_price, change["price_diff"], change["change_type"],
                    date_str
                )

            return self.serialize_document(data)


        except Exception as e:
            raise PriceLoggingError(product_id=str(product_id), error=str(e))


    def log_prices(self, products: list[dict]) -> list[dict]:
        """Log the prices for a list of products."""
        logged_prices = []
        for product in products:
            logged_price = self.log_price(product['_id'])
            logged_prices.append(self.serialize_document(logged_price))

        return logged_prices


    def get_price_history(self, product_id: str) -> list[dict]:
        """Retrieve the price history for a specific product."""
        price_history = self.db.find_pr(product_id)
        return self.serialize_documents(price_history)


    def yield_product_price_history(self, product_id: str) -> Iterator[dict]:
        """Yield the price history for a specific product one by one."""
        return self.db.yield_product_price_history(product_id)


    def find_all_prices(self) -> list[dict]:
        """Retrieve all price logs across all products."""
        prices = self.db.find_all_price_logs()
        return self.serialize_documents(prices)


    def delete_price(self, price_id: str) -> None:
        """Delete a price log entry by its ID."""
        self.db.delete_price(price_id)

