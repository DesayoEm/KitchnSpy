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

        return self.products.find_one({"_id": obj_id})


    def find_all_products(self) -> list[dict]:
        """Retrieve all products, sorted by product name"""
        return  list(
            self.products.find({}).sort('product_name', pymongo.ASCENDING).limit(10)
        )

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
        return documents

    def yield_product_price_history(self, product_id: str):
        """
        Yield serialized price history documents for a product, one by one.
        """
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        cursor = self.price_logs.find({"product_id": obj_id}).sort("date_checked", pymongo.ASCENDING)

        for document in cursor:
            yield self.util.convert_objectid_to_str(document)


    def find_all_price_logs(self) -> list[dict]:
        documents = list(
            self.price_logs.find({})
            .sort("date_checked", pymongo.ASCENDING)
        )
        return documents

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

        return list(self.subscribers.find({"product_id": obj_id}))


    def yield_product_subscribers(self, product_id: str):
        """Yield serialized subscribers for a product, one by one."""
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            raise InvalidIdError(detail=str(e))

        cursor = self.subscribers.find({"product_id": obj_id}).sort("name", pymongo.ASCENDING)

        for document in cursor:
            yield self.util.convert_objectid_to_str(document)


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
