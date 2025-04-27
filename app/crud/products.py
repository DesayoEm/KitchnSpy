from app.core.database.mongo_gateway import MongoGateway
from app.core.database.validation.product import ProductCreate, ProductData, ProductsCreateBatch
from app.core.services.notifications.notifications import NotificationService
from app.core.services.scraper import Scraper
from app.core.utils import Utils
from app.routers.products import subscription_crud


class ProductCrud:
    def __init__(self):
        """
        Initialize ProductCrud with database access, scraping, and utility methods.
        """
        self.db = MongoGateway()
        self.scraper = Scraper(timeout=30, max_retries=3)
        self.util = Utils()
        self.notification_service = NotificationService()


    def add_product(self, data: ProductCreate) -> dict:
        """
        Scrape a product from the given URL and insert it into the database.
        Args:
            data (ProductCreate): Pydantic class containing name and URL of the product to scrape.
        Returns:
            dict: Metadata about the inserted product.
        """
        scraped_product = self.scraper.scrape_product({
            "name": data.name,
            "url": data.url
        })

        validated_product = ProductData.model_validate(scraped_product).model_dump()
        return self.db.insert_product(validated_product)

    def add_products(self, products: ProductsCreateBatch) -> list[dict]:
        """
        Scrape multiple products from a list and insert them into the database.
        Args:
            products (ProductsCreateBatch): Pydantic batch input containing multiple products.
        Returns:
            list[dict]: List of inserted product metadata.
        """

        product_dicts = [product.model_dump() for product in products]
        scraped_products = self.scraper.scrape_products(product_dicts)

        validated_products = [
            ProductData.model_validate(product).model_dump()
            for product in scraped_products
        ]

        self.db.insert_products(validated_products)
        return validated_products


    def find_product(self, product_id: str) -> dict | None:
        """
        Find a single product in the database by its ID.
        Args:
            product_id (str): The MongoDB ObjectId of the product.
        Returns:
            dict | None: The product document or None if not found.
        """
        product = self.db.find_product(product_id)
        return self.util.convert_objectid_to_str(product)


    def find_all_products(self) -> list[dict]:
        """
        Find all products in the database, sorted by product name.
        Returns:
            list[dict]: A list of product documents (limited to 10).
        """
        products = self.db.find_all_products()
        return [
            self.util.convert_objectid_to_str(product) for product in products
        ]


    def update_product(self, product_id: str) -> dict:
        """
        Update an existing product by re-scraping its data.
        Args:
            product_id (str): The MongoDB ObjectId of the product to update.
        Returns:
            dict: Result of the update operation.
        """

        existing = self.db.find_product(product_id)
        updated_scrape = self.scraper.scrape_product({
            "name": existing["name"],
            "url": existing["url"]
        })

        validated_update = ProductData.model_validate(updated_scrape).model_dump()

        required_fields = ["name", "url", "price", "availability", "img_url"]
        if any(validated_update.get(field) is None for field in required_fields):
            return self.db.update_product(product_id, validated_update)
        else:
            return self.db.replace_product(product_id, validated_update)


    def delete_product(self, product_id: str) -> dict:
        """
        Delete a product from the database, including its price history and subscriptions.
        Args:
            product_id (str): The MongoDB ObjectId of the product to delete.
        Returns:
            dict: The result of the product delete operation.
        """

        from app.crud.prices import PricesCrud
        price_crud = PricesCrud()

        price_history = price_crud.get_price_history(product_id)
        for price in price_history:
            price_id = price["_id"]
            price_crud.delete_price(price_id)

        subscriber_list = subscription_crud.find_all_subscribers(product_id)
        for subscriber in subscriber_list:
            email = subscriber['email_address']
            name = subscriber['name']
            product_name = subscriber['product_name']

            self.notification_service.send_product_removed_notification(
                to_email=email, name=name, product_name=product_name
            )

            subscriber_id = subscriber["_id"]
            subscription_crud.delete_subscriber(subscriber_id)

        return self.db.delete_product(product_id)
