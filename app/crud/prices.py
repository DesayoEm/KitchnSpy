from datetime import datetime, timezone
from bson import ObjectId
from app.core.database.mongo_gateway import MongoGateway
from app.core.exceptions import PriceLoggingError, NotFoundError
from app.core.services.scraper import Scraper
from app.crud.products import ProductCrud
from app.core.utils import Utils


class PricesCrud:
    def __init__(self):
        """
        Initialize the PricesCrud with database access, product CRUD operations, and scraper service.
        """
        self.db = MongoGateway()
        self.products = ProductCrud()
        self.scraper = Scraper()
        self.util = Utils()


    def log_price(self, product_id: str) -> None:
        """
        Log the current price of a product by scraping it and comparing it to the existing stored price.

        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Raises:
            NotFoundError: If the product URL cannot be scraped.
            PriceLoggingError: If any error occurs during the price logging process.
        """
        existing = self.db.find_product(product_id)
        current = self.scraper.scrape_product(existing['url'])

        if not current:
            raise NotFoundError(url=existing['url'])

        try:
            previous_price = float(existing["price"].replace("£", "").replace(",", ""))
            current_price = float(current["price"].replace("£", "").replace(",", ""))
            price_diff = current_price - previous_price
            change_dir = "+" if price_diff > 0 else "-"

            data = {
                "product_id": ObjectId(product_id),
                "previous_price": existing["price"],
                "current_price": current["price"],
                "price_diff": price_diff,
                "change_dir": change_dir,
                "date_checked": datetime.now(timezone.utc)
            }

            self.db.insert_price_log(data)

        except Exception as e:
            raise PriceLoggingError(product_id=str(product_id), error=str(e))


    def log_prices(self, products: list[dict]) -> None:
        """
        Log the prices for a list of products.
        Args:
            products (list[dict]): A list of product documents, each containing an '_id' field.
        """

        for product in products:
            self.log_price(product['_id'])

    def get_price_history(self, product_id: str) -> list[dict]:
        """
        Retrieve the price history for a specific product.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Returns:
            list[dict]: List of price history records.
        """
        price_history = self.db.find_price_history(product_id)
        return [
            self.util.convert_objectid_to_str(price) for price in price_history
        ]


    def find_all_prices(self) -> list[dict]:
        """
        Retrieve all price logs across all products.

        Returns:
            list[dict]: List of all price log documents.
        """
        prices = self.db.find_all_price_logs()
        return [
        self.util.convert_objectid_to_str(price) for price in prices
        ]


    def delete_price(self, price_id: str) -> dict:
        """
        Delete a price log entry by its ID.

        Args:
            price_id (str): The MongoDB ObjectId of the price log entry.

        Returns:
            dict: Result of the delete operation.
        """
        return self.db.delete_price(price_id)
