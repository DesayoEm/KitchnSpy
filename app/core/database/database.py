import os
from dotenv import load_dotenv
from datetime import date
from pymongo import MongoClient

from app.core.exceptions import URIConnectionError
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

    def insert_product(self, data: dict):
        return self.products.insert_one(data)

    def insert_products(self, data: dict):
        return self.products.insert_many(data)

    def find_product(self, url: str):
        return self.products.find_one({'url': url})

    def update_product(self, filter: dict, updated_data: dict):
        return self.products.update_one(filter, {"$set": updated_data}, upsert=True)

    def replace_product(self, filter: dict, new_document: dict):
        return self.products.replace_one(filter, new_document)

    def log_price(self, data):
        return self.price_log.insert_one(data)










