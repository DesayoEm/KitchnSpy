import os
import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from app.core.exceptions import URIConnectionError, InvalidIdError

load_dotenv()


class MongoGateway:
    """
    Gateway class for interacting with MongoDB collections:
    products, price_logs, and subscribers.
    """
    def __init__(self):
        """
        Initialize MongoDB connection and collections.
        """
        uri = os.getenv('DB_URI')
        if not uri:
            raise URIConnectionError()

        client = MongoClient(uri)
        db = client['kitchnspy']
        self.products = db["products"]
        self.price_logs = db["price_log"]
        self.subscribers = db["subscribers"]


    # Products
    def insert_product(self, data: dict) -> dict:
        """
        Insert a single product into the database.
        Args:
            data (dict): Product data to insert.

        Returns:
            dict: Inserted product metadata.
        """
        return self.products.insert_one(data)


    def insert_products(self, data: list[dict]) -> dict:
        """
        Insert multiple products into the database.
        Args:
            data (list[dict]): List of product data dictionaries.

        Returns:
            dict: Inserted products metadata.
        """
        return self.products.insert_many(data)


    def find_product(self, product_id: str) -> dict | None:
        """
        Find a single product by its ID.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Returns:
            dict | None: The product document or None if not found.
        """
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.find_one({"_id": obj_id})


    def find_all_products(self) -> list[dict]:
        """
        Retrieve all products, sorted by product name (limited to 10).
        Returns:
            list[dict]: List of product documents.
        """

        return list(
            self.products.find({}, {"_id": 0})
            .sort('product_name', pymongo.ASCENDING)
            .limit(10)
        )


    def update_product(self, product_id: str, updated_data: dict) -> dict:
        """
        Update an existing product with new data.
        Args:
            product_id (str): The MongoDB ObjectId of the product.
            updated_data (dict): Data fields to update.

        Returns:
            dict: Result of the update operation.
        """
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.update_one(
            {"_id": obj_id}, {"$set": updated_data}, upsert=True
        )


    def replace_product(self, product_id: str, new_document: dict) -> dict:
        """
        Replace an entire product document.

        Args:
            product_id (str): The MongoDB ObjectId of the product.
            new_document (dict): New full document to replace with.

        Returns:
            dict: Result of the replace operation.
        """
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.replace_one({"_id": obj_id}, new_document)


    def delete_product(self, product_id: str) -> dict:
        """
        Delete a product by its ID.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Returns:
            dict: Result of the delete operation.
        """
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.delete_one({"_id": obj_id})


    # Pricelogs
    def insert_price_log(self, data: dict) -> dict:
        """
        Insert a price log entry.
        Args:
            data (dict): Price log data.

        Returns:
            dict: Inserted log metadata.
        """
        return self.price_logs.insert_one(data)


    def find_price_history(self, product_id: str) -> list[dict]:
        """
        Find the price history logs for a specific product, sorted by date.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Returns:
            list[dict]: List of price history records sorted by date_checked.
        """
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return list(
            self.price_logs.find({"product_id": obj_id}, {"_id": 0})
            .sort("date_checked", pymongo.ASCENDING)
        )


    def find_all_price_logs(self) -> list[dict]:
        """
        Retrieve all price logs across all products, sorted by date.
        Returns:
            list[dict]: List of all price history entries.
        """

        return list(
            self.price_logs.find({}, {"_id": 0})
            .sort("date_checked", pymongo.ASCENDING)
        )

    def delete_price(self, price_id: str) -> dict:
        """
        Delete a price log by its ID.
        Args:
            price_id (str): The MongoDB ObjectId of the price log.

        Returns:
            dict: Result of the delete operation.
        """
        try:
            obj_id = ObjectId(price_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.price_logs.delete_one({"_id": obj_id})


    #Subscribers
    def insert_subscriber(self, data: dict) -> dict:
        """
        Insert a new subscriber into the database.
        Args:
            data (dict): Subscriber information.

        Returns:
            dict: Inserted subscriber metadata.
        """
        return self.subscribers.insert_one(data)


    def find_subscribers(self, product_id: str) -> list[dict]:
        """
        Find all subscribers for a specific product.
        Args:
            product_id (str): The MongoDB ObjectId of the product.

        Returns:
            list[dict]: List of subscriber documents.
        """
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return list(
            self.subscribers.find({"product_id": obj_id}, {"_id": 0})
        )


    def delete_subscriber(self, subscriber_id: str) -> dict:
        """
        Delete a subscriber by their ID.
        Args:
            subscriber_id (str): The ID of the subscriber.

        Returns:
            dict: Result of the delete operation.
        """
        return self.subscribers.delete_one({'subscriber_id': subscriber_id})
