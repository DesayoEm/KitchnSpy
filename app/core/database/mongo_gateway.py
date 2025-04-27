import os
import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from app.core.exceptions import URIConnectionError, InvalidIdError
from app.core.utils import Utils
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult

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
        self.util = Utils()

    def _serialize_document(self, document: dict | None) -> dict | None:
        """Convert ObjectId to str in a single document."""
        return self.util.convert_objectid_to_str(document)

    def _serialize_documents(self, documents: list[dict]) -> list[dict]:
        """Convert ObjectId to str in a list of documents."""
        return [self.util.convert_objectid_to_str(doc) for doc in documents if doc]


    # Products
    def insert_product(self, data: dict) -> InsertOneResult:
        return self.products.insert_one(data)

    def insert_products(self, data: list[dict]) -> InsertManyResult:
        return self.products.insert_many(data)

    def find_product(self, product_id: str) -> dict | None:
        """Find a single product by its ID."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        document = self.products.find_one({"_id": obj_id})
        return self._serialize_document(document)


    def find_all_products(self) -> list[dict]:
        """Retrieve all products, sorted by product name (limited to 10)."""
        documents = list(
            self.products.find({}).sort('product_name', pymongo.ASCENDING).limit(10)
        )
        return self._serialize_documents(documents)


    def update_product(self, product_id: str, updated_data: dict) -> UpdateResult:
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.update_one(
            {"_id": obj_id},
            {"$set": updated_data},
            upsert=True
        )

    def replace_product(self, product_id: str, new_document: dict) -> UpdateResult:
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.replace_one({"_id": obj_id}, new_document)

    def delete_product(self, product_id: str) -> DeleteResult:
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.products.delete_one({"_id": obj_id})


    # Pricelogs
    def insert_price_log(self, data: dict) -> InsertOneResult:
        return self.price_logs.insert_one(data)

    def find_price_history(self, product_id: str) -> list[dict]:
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        documents = list(
            self.price_logs.find({"product_id": obj_id})
            .sort("date_checked", pymongo.ASCENDING)
        )
        return self._serialize_documents(documents)

    def find_all_price_logs(self) -> list[dict]:
        documents = list(
            self.price_logs.find({})
            .sort("date_checked", pymongo.ASCENDING)
        )
        return self._serialize_documents(documents)

    def delete_price(self, price_id: str) -> DeleteResult:
        try:
            obj_id = ObjectId(price_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.price_logs.delete_one({"_id": obj_id})



    #Subscriptions
    def insert_subscriber(self, data: dict) -> InsertOneResult:
        return self.subscribers.insert_one(data)

    def find_subscribers(self, product_id: str) -> list[dict]:
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        documents = list(self.subscribers.find({"product_id": obj_id}))
        return self._serialize_documents(documents)

    def find_subscriber(self, email_address: str, product_id: str) -> dict | None:
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        document = self.subscribers.find_one({
            "product_id": obj_id,
            "email_address": email_address
        })
        return self._serialize_document(document)

    def delete_subscriber(self, subscriber_id: str) -> DeleteResult:
        try:
            obj_id = ObjectId(subscriber_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        return self.subscribers.delete_one({"_id": obj_id})
