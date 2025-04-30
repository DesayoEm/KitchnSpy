from app.infra.db.adapters.shared_imports import *
from app.infra.db.adapters.base_adapter import BaseAdapter

load_dotenv()

class PriceLogAdapter(BaseAdapter):
    def insert_price_log(self, data: dict) -> None:
        """Insert a single price log document into the price_logs collection."""

        try:
            result = self.price_logs.insert_one(data)
            logger.info(f"Inserted price log with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Failed to insert price log: {str(e)}")
            raise


    def yield_product_price_history(self, product_id: str) -> Generator[Dict, None, None]:
        """Yield serialized price history documents for a specific product."""
        try:
            cursor = self.price_logs.find({"product_id": product_id})
            yield from self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error yielding price history for product {product_id}: {str(e)}")
            raise


    def yield_and_paginate_product_price_history(
        self, product_id: str, page: int = 1, per_page: int = 20
    ) -> Generator[Dict, None, None]:
        """
        Yield serialized price history documents for a specific product, paginated.
        Args:
            product_id: The ID of the product to fetch price logs for.
            page: Page number (1-based).
            per_page: Number of documents per page.
        Yields:
            Serialized price log documents as dictionaries.
        """
        try:
            skip = (page - 1) * per_page if page > 0 else 0
            cursor = self.price_logs.find({"product_id": product_id}) \
                .sort("date_checked", pymongo.ASCENDING) \
                .skip(skip).limit(per_page)

            yield from self.yield_documents(cursor)
        except Exception as e:
            logger.error(f"Error yielding price history for product {product_id}: {str(e)}")
            raise



    def yield_and_paginate_all_price_logs(
        self, page: int = 1, per_page: int = 20
    ) -> Generator[Dict, None, None]:
        """
        Yield serialized price history documents for all products, paginated.
        Args:
            page: Page number (1-based).
            per_page: Number of documents per page.
        Yields:
            Serialized price log documents as dictionaries.
        """
        try:
            skip = (page - 1) * per_page if page > 0 else 0
            cursor = self.price_logs.find({}) \
                .sort("date_checked", pymongo.ASCENDING) \
                .skip(skip).limit(per_page)

            yield from self.yield_documents(cursor)
        except Exception as e:
            logger.error(f"Error yielding price history for products: {str(e)}")
            raise




    def delete_price(self, price_id: str) -> None:
        """Delete a price log document by its ID"""
        obj_id = self.validate_obj_id(price_id, "Price log")

        try:
            result = self.price_logs.delete_one({"_id": obj_id})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Deleted price log {price_id}")
            else:
                raise DocNotFoundError(identifier=price_id, entity="Price")
        except Exception as e:
            logger.error(f"Error deleting price log {price_id}: {str(e)}")
            raise
