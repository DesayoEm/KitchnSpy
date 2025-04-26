from datetime import datetime, timezone
from bson import ObjectId
from app.core.database.mongo_gateway import MongoGateway
from app.core.exceptions import PriceLoggingError, NotFoundError
from app.core.services.scraper import Scraper
from app.crud.products import ProductCrud


class HistoryCrud:
    def __init__(self):
        """
        Initialize the HistoryCrud with database access, product CRUD operations, and scraper service.
        """
        self.db = MongoGateway()
        self.products = ProductCrud()
        self.scraper = Scraper()


    def log_price(self, product_id: str) -> None:
        """
        Log the current price of a product by scraping it and comparing it to the existing stored price.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Raises:
            NotFoundError: If the product URL cannot be scraped.
            PriceLoggingError: If there is any error during the price logging process.
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
