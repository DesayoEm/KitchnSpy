import os
import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from app.core.exceptions import URIConnectionError, InvalidIdError, DocNotFoundError
from app.core.utils import Utils
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult

load_dotenv()


class MongoGateway:
    """
    Gateway class for interacting with MongoDB collections:
    products, price_logs, and subscribers.
    """

    def __init__(self):
        """Initialize MongoDB connection and collections."""
        uri = os.getenv('DB_URI')
        if not uri:
            raise URIConnectionError()

        client = MongoClient(uri)
        db = client['kitchnspy']
        self.products = db["products"]
        self.price_logs = db["price_log"]
        self.subscribers = db["subscribers"]
        self.util = Utils()

    # Products

    def insert_product(self, data: dict) -> InsertOneResult:
        """Insert a single product document into the database."""
        return self.products.insert_one(data)

    def insert_products(self, data: list[dict]) -> InsertManyResult:
        """Insert multiple product documents into the database."""
        return self.products.insert_many(data)

    def find_product(self, product_id: str) -> dict:
        """Find a single product by its ID."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        product = self.products.find_one({"_id": obj_id})
        if product is None:
            raise DocNotFoundError(identifier=product_id, entity="Product")

        return product

    def find_all_products(self) -> list[dict]:
        """Retrieve all products, sorted by product name."""
        return list(self.products.find({}).sort('product_name', pymongo.ASCENDING).limit(10))

    def update_product(self, product_id: str, updated_data: dict) -> UpdateResult:
        """Update fields of an existing product document."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.update_one({"_id": obj_id}, {"$set": updated_data}, upsert=True)

    def replace_product(self, product_id: str, new_document: dict) -> UpdateResult:
        """Replace an entire product document."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.replace_one({"_id": obj_id}, new_document)

    def delete_product(self, product_id: str) -> None:
        """Delete a product document by its ID."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        self.products.delete_one({"_id": obj_id})

    # Price Logs

    def insert_price_log(self, data: dict) -> InsertOneResult:
        """Insert a single price log document into the database."""
        return self.price_logs.insert_one(data)

    def find_price_history(self, product_id: str) -> list[dict]:
        """Retrieve the price history documents for a product."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        documents = list(self.price_logs.find({"product_id": obj_id}).sort("date_checked", pymongo.ASCENDING))
        if not documents:
            raise DocNotFoundError(identifier=product_id, entity="Price history")
        return documents

    def yield_product_price_history(self, product_id: str):
        """Yield serialized price history documents for a product one by one."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        cursor = self.price_logs.find({"product_id": obj_id}).sort("date_checked", pymongo.ASCENDING)
        for document in cursor:
            yield self.util.convert_objectid_to_str(document)

    def find_all_price_logs(self) -> list[dict]:
        """Retrieve all price logs, sorted by date checked."""
        return list(self.price_logs.find({}).sort("date_checked", pymongo.ASCENDING))

    def delete_price(self, price_id: str) -> None:
        """Delete a price log document by its ID."""
        try:
            obj_id = ObjectId(price_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        self.price_logs.delete_one({"_id": obj_id})

    # Subscribers

    def insert_subscriber(self, data: dict) -> InsertOneResult:
        """Insert a single subscriber document into the database."""
        return self.subscribers.insert_one(data)

    def find_subscribers(self, product_id: str) -> list[dict]:
        """Retrieve all subscribers for a given product."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        subscribers = list(self.subscribers.find({"product_id": obj_id}))
        if not subscribers:
            raise DocNotFoundError(identifier=product_id, entity="Subscribers")
        return subscribers

    def yield_product_subscribers(self, product_id: str):
        """Yield serialized subscriber documents for a product one by one."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        cursor = self.subscribers.find({"product_id": obj_id}).sort("name", pymongo.ASCENDING)
        for document in cursor:
            yield self.util.convert_objectid_to_str(document)

    def find_subscriber(self, email_address: str, product_id: str) -> dict:
        """Find a single subscriber by email address and product ID."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        subscriber = self.subscribers.find_one({"product_id": obj_id, "email_address": email_address})
        if subscriber is None:
            raise DocNotFoundError(identifier=email_address, entity="Subscriber")

        return subscriber

    def delete_subscriber(self, subscriber_id: str) -> None:
        """Delete a subscriber document by its ID."""
        try:
            obj_id = ObjectId(subscriber_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        self.subscribers.delete_one({"_id": obj_id})
