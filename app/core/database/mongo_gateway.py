import os
import pymongo
from dotenv import load_dotenv
from datetime import date
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from app.core.exceptions import URIConnectionError, InvalidIdError

load_dotenv()


class MongoGateway:
    def __init__(self):
        uri = os.getenv('DB_URI')
        if not uri:
            raise URIConnectionError()

        client = MongoClient(uri)
        db = client['kitchnspy']
        self. products = db["products"]
        self.price_log = db["price_log"]
        self.subscribers = db["subscribers"]

    #Products
    def insert_product(self, data: dict):
        return self.products.insert_one(data)

    def insert_products(self, data: list[dict]):
        return self.products.insert_many(data)

    def find_product(self, product_id: str):
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            return InvalidIdError(detail = str(e))

        return self.products.find_one({"_id": obj_id})

    def find_all_products(self):
        return (
            self.products.find({}, {"_id": 0})
            .sort('product_name', pymongo.ASCENDING)
            .limit(10)
        )

    def update_product(self, product_id: str, updated_data: dict):
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            return InvalidIdError(detail = str(e))

        return self.products.update_one(
            {"_id":obj_id}, {"$set": updated_data}, upsert=True
        )

    def replace_product(self, product_id: str, new_document: dict):
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            return InvalidIdError(detail = str(e))

        return self.products.replace_one(
        {"_id":obj_id}, new_document
        )


    def delete_product(self, product_id: str):
        try:
            obj_id = ObjectId(product_id)
        except InvalidId as e:
            return InvalidIdError(detail = str(e))

        return self.products.delete_one({"_id":obj_id})



    #Price logs
    def insert_price_log(self, data):
        return self.price_log.insert_one(data)

    def find_price_log(self, filter: dict):
        pass


    #Subscribers
    def insert_subscriber(self, data: dict):
        return self.subscribers.insert_one(data)

    def delete_subscriber(self, email: str):
        return self.subscribers.delete_one({'email_address': email})










