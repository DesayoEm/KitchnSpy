from app.core.database.mongo_gateway import MongoGateway
from app.core.database.validation.product import ProductCreate, ProductData, ProductsCreateBatch
from app.core.exceptions import DocsNotFoundError
from app.core.services.notifications.notifications import NotificationService
from app.core.services.scraper import Scraper
from app.core.utils import Utils


class ProductCrud:
    def __init__(self):
        """
        Initialize ProductCrud with database access, scraping, and utility methods.
        """
        self.db = MongoGateway()
        self.scraper = Scraper(timeout=30, max_retries=3)
        self.util = Utils()
        self.notification_service = NotificationService()

    def serialize_document(self, document: dict | None) -> dict | None:
        """Convert ObjectId to str in a single document."""
        if document:
            return self.util.convert_objectid_to_str(document)

    def serialize_documents(self, documents: list[dict]) -> list[dict]:
        """Convert ObjectId to str in a list of documents."""
        if documents:
            return [self.util.convert_objectid_to_str(doc) for doc in documents if doc]


    def add_product(self, data: ProductCreate) -> dict:
        """Scrape a product from the given name and URL and insert it into the database."""

        scraped_product = self.scraper.scrape_product({
            "name": data.name,
            "url": data.url
        })

        validated_product = ProductData.model_validate(scraped_product).model_dump()
        self.db.insert_product(validated_product)

        return self.serialize_document(validated_product)


    def add_products(self, data: ProductsCreateBatch) -> list[dict]:
        """Scrape multiple products from a list and insert them into the database."""
        products = data.products
        product_dicts = [product.model_dump() for product in products]
        scraped_products = self.scraper.scrape_products(product_dicts)

        validated_products = [
            ProductData.model_validate(product).model_dump()
            for product in scraped_products
        ]

        self.db.insert_or_update_products(validated_products)
        return self.serialize_documents(validated_products)


    def find_product(self, product_id: str) -> dict | None:
        """Find a single product in the database by its ID."""
        product = self.db.find_product(product_id)
        return self.serialize_document(product)

    def search_products_by_name(self, search_term: str):
        """Search products by name."""
        return self.db.search_products_by_name(search_term)


    def find_all_products(self) -> list[dict]:
        """Find all products in the database, sorted by product name."""
        products = self.db.find_all_products()
        return self.serialize_documents(products)

    def update_or_replace_product(self, product_id: str) -> dict:
        """Update or replace an existing product by re-scraping its data."""

        existing = self.db.find_product(product_id)
        new_document = self.scraper.scrape_product({
            "name": existing["name"],
            "url": existing["url"]
        })

        validated_update = ProductData.model_validate(new_document).model_dump()

        required_fields = ["product_name", "price", "availability", "img_url"]

        if any(validated_update.get(field) is None for field in required_fields):
            updated_data = self.db.update_product(product_id, validated_update)
            return self.serialize_document(updated_data)
        else:
            updated_data = self.db.replace_product(product_id, validated_update)
            return self.serialize_document(updated_data)


    def delete_product(self, product_id: str) -> None:
        """Delete a product from the database, including its price history and subscriptions."""
        from app.crud.subscription import SubscriptionCrud
        subscription_crud = SubscriptionCrud()

        from app.crud.prices import PricesCrud
        price_crud = PricesCrud()

        price_history = price_crud.yield_product_price_history(product_id)
        for price in price_history:
            price_id = price["_id"]
            price_crud.delete_price(price_id)

        subscribers = subscription_crud.yield_product_subscribers(product_id)
        for subscriber in subscribers:
            email = subscriber['email_address']
            name = subscriber['name']
            product_name = subscriber['product_name']

            self.notification_service.send_product_removed_notification(
                to_email=email, name=name, product_name=product_name
            )

            subscriber_id = subscriber["_id"]
            subscription_crud.delete_subscriber(subscriber_id)

        self.db.delete_product(product_id)
