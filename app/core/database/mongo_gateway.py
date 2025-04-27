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
        """Insert a single product into the database."""
        return self.products.insert_one(data)


    def insert_products(self, data: list[dict]) -> dict:
        """Insert multiple products into the database."""
        return self.products.insert_many(data)


    def find_product(self, product_id: str) -> dict | None:
        """Find a single product by its ID."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.find_one({"_id": obj_id})


    def find_all_products(self) -> list[dict]:
        """Retrieve all products, sorted by product name (limited to 10)."""

        return list(
            self.products.find({}, {"_id": 0})
            .sort('product_name', pymongo.ASCENDING)
            .limit(10)
        )

    def update_product(self, product_id: str, updated_data: dict) -> dict:
        """Update an existing product with new data."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.update_one(
            {"_id": obj_id}, {"$set": updated_data}, upsert=True
                )


    def replace_product(self, product_id: str, new_document: dict) -> dict:
        """Replace an entire product document."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.replace_one({"_id": obj_id}, new_document)


    def delete_product(self, product_id: str) -> dict:
        """Delete a product by its ID."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.delete_one({"_id": obj_id})


    # Pricelogs
    def insert_price_log(self, data: dict) -> dict:
        """Insert a price log entry."""

        return self.price_logs.insert_one(data)


    def find_price_history(self, product_id: str) -> list[dict]:
        """Find the price history logs for a specific product, sorted by date."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return list(
            self.price_logs.find({"product_id": obj_id}, {"_id": 0})
            .sort("date_checked", pymongo.ASCENDING)
        )


    def find_all_price_logs(self) -> list[dict]:
        """Retrieve all price logs across all products, sorted by date."""

        return list(
            self.price_logs.find({}, {"_id": 0})
            .sort("date_checked", pymongo.ASCENDING)
        )

    def delete_price(self, price_id: str) -> dict:
        """Delete a price log by its ID."""
        try:
            obj_id = ObjectId(price_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.price_logs.delete_one({"_id": obj_id})


    #Subscription
    def insert_subscriber(self, data: dict) -> dict:
        """Insert a new subscriber into the database."""
        return self.subscribers.insert_one(data)


    def find_subscribers(self, product_id: str) -> list[dict]:
        """Find all subscribers for a specific product."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return list(
            self.subscribers.find({"product_id": obj_id}, {"_id": 0})
        )


    def find_subscriber(self, email_address: str, product_id: str) -> [dict]:
        """Find a subscriber by product ID and email address."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        self.subscribers.find_one({
            "product_id": obj_id,
            "email_address": email_address
        })


    def delete_subscriber(self, subscriber_id: str) -> dict:
        """Delete a subscriber by their ID."""

        return self.subscribers.delete_one({'subscriber_id': subscriber_id})
