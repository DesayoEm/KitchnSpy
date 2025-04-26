from app.core.database.mongo_gateway import MongoGateway
from app.core.services.scraper import Scraper


class ProductCrud:
    def __init__(self):
        """
        Initialize ProductCrud with database access and scraper service.
        """
        self.db = MongoGateway()
        self.scraper = Scraper(timeout=30, max_retries=3)


    def add_product(self, url: str) -> dict:
        """
        Scrape a product from the given URL and insert it into the database.
        Args:
            url (str): The URL of the product to scrape.

        Returns:
            dict: The inserted product data.
        """
        scraped_product = self.scraper.scrape_product(url)
        return self.db.insert_product(scraped_product)


    def add_products(self, urls: list[dict]) -> list[dict]:
        """
        Scrape multiple products from a list and insert them into the database.
        Args:
            urls (list[dict]): A list of dictionaries containing the product URL to scrape.

        Returns:
            list[dict]: List of inserted product data.
        """
        scraped_products = self.scraper.scrape_all_products(urls)
        self.db.insert_products(scraped_products)
        return scraped_products


    def find_product(self, product_id: str) -> dict:
        """
        Find a single product in the database by its ID.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Returns:
            dict: The product document, or None if not found.
        """
        return self.db.find_product(product_id)


    def find_products(self) -> list[dict]:
        """
        Find all products in the database, sorted by product name.
        Returns:
            list[dict]: A list of product documents (limited to 10).
        """
        return self.db.find_all_products()


    def update_product(self, product_id: str) -> dict:
        """
        Update an existing product by re-scraping its data.
        Args:
            product_id (str): The MongoDB ObjectId of the product to update.

        Returns:
            dict: The result of the update operation.
        """
        existing = self.db.find_product(product_id)
        updated_data = self.scraper.scrape_product(existing["url"])

        required_fields = ["name", "url", "price", "availability", "img_url"]
        if any(updated_data.get(field) is None for field in required_fields):
            return self.db.update_product(product_id, updated_data)
        else:
            return self.db.replace_product(product_id, updated_data)


    def delete_product(self, product_id: str) -> dict:
        """
        Delete a product from the database by its product ID.
        Args:
            product_id (str): The MongoDB ObjectId of the product to delete.

        Returns:
            dict: The result of the delete operation.
        """
        return self.db.delete_product(product_id)
