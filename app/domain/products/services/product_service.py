from app.infra.db.adapters.product_adapter import ProductAdapter
from app.domain.products.schema import ProductCreate, ProductData, ProductsCreateBatch, ProductsUpdateBatch
from app.shared.exceptions import DocsNotFoundError, FailedRequestError
from app.domain.subscribers.services.notification_service import NotificationService
from app.infra.scraping.kitchenaid_scraper import Scraper
from app.shared.serializer import Serializer
from typing import List, Dict

from app.infra.log_service import logger


class ProductService:
    def __init__(self):
        """
        Initialize ProductService with database access, scraping, and utility methods.
        """
        self.db = ProductAdapter()
        self.scraper = Scraper(timeout=30, max_retries=3)
        self.serializer = Serializer()
        self.notification_service = NotificationService()



    def add_product(self, data: ProductCreate) -> dict:
        """Scrape a product from the given name and URL and insert it into the database."""

        scraped_product = self.scraper.scrape_product({
            "name": data.name,
            "url": data.url
        })

        validated_product = ProductData.model_validate(scraped_product).model_dump()
        self.db.insert_product(validated_product)

        return self.serializer.json_serialize_doc(validated_product)


    def add_products(self, data: ProductsCreateBatch) -> List[Dict]:
        """Scrape multiple products from a list and insert them into the database."""
        products = data.products
        product_dicts = [product.model_dump() for product in products]
        scraped_products = self.scraper.scrape_products(product_dicts)

        validated_products = [
            ProductData.model_validate(product).model_dump()
            for product in scraped_products
        ]

        self.db.insert_or_update_products(validated_products)
        return self.serializer.json_serialize_docs(validated_products)


    def compile_product_ids(self) -> List[str]:
        """Compile all product IDs in a list"""
        return self.db.compile_product_ids()


    def find_product(self, product_id: str) -> Dict | None:
        """Find a single product in the database by its ID."""
        product = self.db.find_product(product_id)
        return self.serializer.json_serialize_doc(product)


    def search_products_by_name(self, search_term: str) -> List[Dict]:
        """Search products by name."""
        return self.db.search_products_by_name(search_term)


    def find_all_products(self) -> List[Dict]:
        """Find all products in the database, sorted by product name."""
        products = self.db.find_products_paginated()
        return self.serializer.json_serialize_docs(products)


    def replace_product(self, product_id: str) -> Dict:
        """Update or replace an existing product by re-scraping its data."""

        existing = self.db.find_product(product_id)
        new_document = self.scraper.scrape_product({
            "name": existing["name"],
            "url": existing["url"]
        })

        validated_update = ProductData.model_validate(new_document).model_dump()

        updated_data = self.db.replace_product(product_id, validated_update)
        return self.serializer.json_serialize_doc(updated_data)


    def bulk_replace_products(self, data: ProductsUpdateBatch) -> str:
        """Bulk update fields for existing product documents."""
        operations = []

        for product in data.products:
            try:
                existing = self.db.find_product_by_url(product.url)
                new_document = self.scraper.scrape_product({
                    "name": existing["name"],
                    "url": existing["url"]
                })

                validated = ProductData.model_validate(new_document).model_dump()
                operations.append({
                    "filter": {"_id": existing["_id"]},
                    "replacement": validated
                })


            except (DocsNotFoundError, FailedRequestError) as e:
                logger.info(f"Skipping URL {product.url}: {e}")
                continue

            updated_count = self.db.bulk_replace_products(operations)
            return f"Updated {updated_count} products"

        logger.info("No products updated")
        return f"Updated 0 products"


    def delete_product(self, product_id: str) -> None:
        """Delete a product from the database, including its price history and subscriptions."""
        from app.domain.subscribers.services.subscription_service import SubscriptionService
        subscription_crud = SubscriptionService()

        obj_id = self.db.validate_obj_id(product_id, "Product")
        self.db.price_logs.delete_many({"product_id": obj_id})
        logger.info(f"Deleted price logs for product {product_id}")

        subscribers = subscription_crud.yield_product_subscribers(product_id)
        for subscriber in subscribers:
            try:
                email = subscriber['email_address']
                name = subscriber['name']
                product_name = subscriber['product_name']

                self.notification_service.send_product_removed_notification(
                    to_email=email, name=name, product_name=product_name
                )

                subscription_crud.delete_subscriber(subscriber["_id"])
            except Exception as e:
                logger.error(f"Failed to notify or delete subscriber {subscriber['_id']}: {str(e)}")

        self.db.delete_product(product_id)
