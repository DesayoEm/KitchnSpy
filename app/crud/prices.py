from datetime import datetime, timezone, timedelta
from bson import ObjectId
from app.core.database.mongo_gateway import MongoGateway
from app.core.exceptions import URLNotFoundError
from app.core.services.price_change import PriceChangeService
from app.core.services.scraper import Scraper
from app.crud.products import ProductCrud
from app.core.utils import Utils
from typing import Iterator

from app.infra.log_service import logger


class PricesCrud:
    def __init__(self):
        """
        Initialize the PricesCrud with database access, product CRUD operations, and scraper service.
        """
        self.db = MongoGateway()
        self.products = ProductCrud()
        self.scraper = Scraper()
        self.util = Utils()
        self.price_service = PriceChangeService()

    def serialize_document(self, document: dict | None) -> dict | None:
        """Convert ObjectId to str in a single document."""
        if document:
            return self.util.json_serialize_doc(document)

    def serialize_documents(self, documents: list[dict]) -> list[dict]:
        """Convert ObjectId to str in a list of documents."""
        if documents:
            return [self.util.json_serialize_doc(doc) for doc in documents if doc]

    def log_price(self, product_id: str) -> dict:
        """Log the current price of a product by scraping it and comparing it to the existing stored price."""
        existing = self.db.find_product(product_id)
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

            change = self.price_service.detect_change(previous_price, new_price)

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
                self.price_service.notify_subscribers(
                    product_id, previous_price, new_price, change["price_diff"], change["change_type"],
                    date_str
                )

            return self.serialize_document(data)

        except Exception:
            raise

    def log_prices(self) -> dict:
        """Log prices for all products and return a summary."""
        updated_count = 0
        error_count = 0

        product_ids = self.db.compile_product_ids()

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


    def yield_all_prices(self, page: int, per_page: int) -> Iterator[dict]:
        """Yield all price logs across all products."""
        return self.db.yield_and_paginate_all_price_logs(page, per_page)

    def yield_product_price_history(self, product_id: str, page: int, per_page: int) -> Iterator[dict]:
        """Yield the price history for a specific product one by one."""
        return self.db.yield_and_paginate_product_price_history(product_id, page, per_page)

    def delete_price(self, price_id: str) -> None:
        """Delete a price log entry by its ID."""
        self.db.delete_price(price_id)

    def delete_old_price_logs(self) -> int:
        """Delete all price log entries older than 1 year ago."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(minutes=1)

        result = self.db.price_logs.delete_many({
            "date_checked": {"$lt": cutoff_date}
        })
        deleted_count = result.deleted_count
        logger.info(f"{deleted_count} price logs deleted")
        return deleted_count



