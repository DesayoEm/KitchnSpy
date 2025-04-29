import os
import pymongo
import re
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from app.infra.log_service import logger
from app.core.exceptions import (
    URIConnectionError, InvalidIdError, DocNotFoundError, DocsNotFoundError,
    EmptySearchError, ExistingSubscriptionError
)
from app.core.utils import Utils
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult
from contextlib import contextmanager
from typing import Generator, Optional, Any, List, Dict
load_dotenv()



class MongoGateway:
    """
    Gateway class for interacting with MongoDB collections:
    """

    def __init__(self):
        """Initialize MongoDB connection and collections."""
        uri = os.getenv('DB_URI')
        if not uri:
            raise URIConnectionError()
        try:
            client = MongoClient(uri)
            db = client['kitchnspy']
            self.products = db["products"]
            self.price_logs = db["price_log"]
            self.subscribers = db["subscribers"]
            self.util = Utils()
            self.ensure_indexes()

            logger.info("MongoDB connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def ensure_indexes(self):
        self.products.create_index([("product_name", pymongo.ASCENDING)])
        self.price_logs.create_index([("product_id", pymongo.ASCENDING),
                    ("date_checked", pymongo.ASCENDING)]
            )
        self.subscribers.create_index([("product_id", pymongo.ASCENDING)])
        self.subscribers.create_index([("email_address", pymongo.ASCENDING),
                    ("product_id", pymongo.ASCENDING)], unique=True
            )

    @staticmethod
    def validate_obj_id(id_str: str, entity_name: str = "Document")-> ObjectId:
        """Validate and convert string ID to ObjectId."""
        try:
            return ObjectId(id_str)
        except InvalidId as e:
            raise InvalidIdError(entity =entity_name, detail=str(e))

    def find_by_id(self, collection, doc_id: str , entity_name: str):
        """Find a document by its ID in the specified collection."""
        obj_id = self.validate_obj_id(doc_id, entity_name)
        document = collection.find_one({"_id":obj_id})
        if not document:
            raise DocNotFoundError(identifier=doc_id, entity=entity_name)

        return document

    def yield_documents(self, cursor)-> Generator[Dict, None, None]:
        """Yield serialized documents one by one."""
        for document in cursor:
            yield self.util.convert_objectid_to_str(document)

    @staticmethod
    def paginate_results(cursor, page: int = 1, per_page: int = 10)-> List[Dict]:
        """Paginate results from a cursor."""
        skip = (page - 1) * per_page if page > 0 else 0
        return list(cursor.skip(skip).limit(per_page))


    #Products
    def insert_product(self, data: dict) -> InsertOneResult:
        """Insert a single product document into the database."""
        try:
            result = self.products.insert_one(data)
            logger.info(f"Inserted product with ID: {result.inserted_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to insert product: {str(e)}")
            raise


    def insert_products(self, data: list[dict]) -> InsertManyResult:
        """Insert multiple product documents into the database."""
        try:
            result = self.products.insert_many(data)
            logger.info(f"Inserted {len(result.inserted_ids)} products")
            return result
        except Exception as e:
            logger.error(f"Failed to insert products: {str(e)}")
            raise


    def find_product(self, product_id: str) -> dict:
        """Find a single product by its ID."""
        return self.find_by_id(self.products, product_id, "Product")


    def find_all_products(self, page: int = 1) -> list[dict]:
        """Retrieve all products with pagination."""

        try:
            cursor = self.products.find({}).sort("product_name", pymongo.ASCENDING)
            products = self.paginate_results(cursor, page, 10)

            if not products:
                raise DocsNotFoundError(entities="Products", page = page)
            return products

        except Exception as e:
            if not isinstance(e, DocsNotFoundError):
                logger.error(f"Error retrieving products: {str(e)}")
                raise


    def search_products_by_name(self, search_term: str, page: int = 1, per_page: int=10):
        """Search products by name with pagination."""
        search_term = search_term.strip()
        if not search_term:
            raise EmptySearchError(entry=search_term)

        try:
            safe_search = re.escape(search_term)
            cursor = self.products.find({
            "$or": [
                {"name": {"$regex": safe_search,"$options": "i"}},
                {"product_name": {"$regex": safe_search, "$options": "i"}}
            ]
            }).sort("product_name", pymongo.ASCENDING)

            skip = (page - 1) * per_page if page > 0 else 0
            cursor = cursor.skip(skip).limit(per_page)
            yield from self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            raise


    def update_product(self, product_id: str, new_document: dict) -> dict:
        """Update fields of an existing product document."""
        obj_id = self.validate_obj_id(product_id, "Product")
        try:
            if not self.products.find_one({"_id": obj_id}):
                raise DocNotFoundError(identifier=product_id, entity="Product")

            result = self.products.replace_one({"_id": obj_id}, new_document)
            if result.modified_count == 0:
                logger.info(f"No changes made when updating product {product_id}")

            logger.info(f"Updated product {product_id}")
            updated_document = self.find_product(product_id)
            return updated_document

        except Exception as e:
            if not isinstance(e, DocNotFoundError):
                logger.error(f"Error replacing product {product_id}: {str(e)}")
            raise


    def bulk_update_products(self, products: List[Dict[str, Any]]) -> int:
        operations = []
        for product in products:
            obj_id = self.validate_obj_id(product['_id'], "Product")
            operations.append(
                pymongo.UpdateOne(
                    {"_id": obj_id},
                    {"$set": product['data']}
                )
            )

            if operations:
                result = self.products.bulk_write(operations)
                logger.info(f"Bulk updated {result.modified_count} products")
                return result.modified_count
            return 0


    def replace_product(self, product_id: str, new_document: dict) -> dict:
        """Replace an entire product document."""
        obj_id = self.validate_obj_id(product_id, "Product")

        try:
            if not self.products.find_one({"_id": obj_id}):
                raise DocNotFoundError(identifier=product_id, entity="Product")

            result = self.products.replace_one({"_id": obj_id}, new_document)
            if result.modified_count == 0:
                logger.info(f"No changes made when updating product {product_id}")
            logger.info(f"Replaced product {product_id}")

            replaced_document = self.find_product(product_id)
            return replaced_document

        except Exception as e:
            if not isinstance(e, DocNotFoundError):
                logger.error(f"Error replacing product {product_id}: {str(e)}")
            raise


    def delete_product(self, product_id: str) -> None:
        """Delete a product document by its ID."""
        obj_id = self.validate_obj_id(product_id, "Product")

        try:
            result = self.products.delete_one({"_id": obj_id})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Deleted product {product_id}")
            else:
                raise DocNotFoundError(identifier=product_id, entity="Product")

        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise



    # Price Logs
    def insert_price_log(self, data: dict) -> InsertOneResult:
        """Insert a single price log document into the database."""
        try:
            result = self.price_logs.insert_one(data)
            logger.info(f"Inserted price log with ID: {result.inserted_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to insert price log: {str(e)}")
            raise


    def yield_product_price_history(self, product_id: str) -> Generator[Dict, None, None]:
        """Yield serialized price history documents for a product one by one with pagination."""

        obj_id = self.validate_obj_id(product_id, "Product")
        try:
            cursor = self.price_logs.find({"product_id": obj_id})
            return self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error yielding price history for product {product_id}: {str(e)}")
            raise


    def yield_and_paginate_product_price_history(
            self, product_id: str, page: int = 1, per_page: int = 20
        ) -> Generator[Dict, None, None]:

        """Yield serialized price history documents for a product one by one with pagination."""
        obj_id = self.validate_obj_id(product_id, "Product")

        try:
            skip = (page - 1) * per_page if page > 0 else 0
            cursor = self.price_logs.find({"product_id": obj_id}) \
                .sort("date_checked", pymongo.ASCENDING) \
                .skip(skip).limit(per_page)

            yield from self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error yielding price history for product {product_id}: {str(e)}")
            raise


    def find_all_price_logs(self, page: int = 1, per_page: int = 20) -> list[dict]:
        """Retrieve all price logs with pagination, sorted by date checked."""
        try:
            cursor = self.price_logs.find({}).sort("date_checked", pymongo.ASCENDING)
            return self.paginate_results(cursor, page, per_page)

        except Exception as e:
            logger.error(f"Error retrieving price logs: {str(e)}")
            raise


    def delete_price(self, price_id: str) -> None:
        """Delete a price log document by its ID"""
        obj_id = self.validate_obj_id(price_id, "Price log")

        try:
            result = self.price_logs.delete_one({"_id": obj_id})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Deleted price log {price_id}")
            else:
                raise DocNotFoundError(identifier=price_id, entity="Price")
        except Exception as e:
            logger.error(f"Error deleting price log {price_id}: {str(e)}")
            raise



    #subscribers
    def insert_subscriber(self, data: dict) -> InsertOneResult:
        """Insert a single subscriber document into the database."""
        try:
            result = self.subscribers.insert_one(data)
            logger.info(f"Inserted subscriber with ID: {result.inserted_id}")
            return result
        except DuplicateKeyError:
            raise ExistingSubscriptionError(
                email_address=data.get('email_address'), product_id=data.get('product_id')
            )

        except Exception as e:
            logger.error(f"Failed to insert subscriber: {str(e)}")
            raise


    def find_subscribers(self, product_id: str, page: int = 1, per_page: int = 20) -> list[dict]:
        """Retrieve all subscribers for a given product with pagination."""
        obj_id = self.validate_obj_id(product_id, "Product")

        try:
            cursor = self.subscribers.find(
                {"product_id": obj_id}).sort("email_address", pymongo.ASCENDING
                    )
            subscribers = self.paginate_results(cursor, page, per_page)

            if not subscribers:
                raise DocsNotFoundError(entities="Subscribers", page = page)
            return subscribers

        except Exception as e:
            if not isinstance(e, DocNotFoundError):
                logger.error(f"Error retrieving subscribers for product {product_id}: {str(e)}")
            raise


    def yield_product_subscribers(self, product_id: str) -> Generator[
        Dict, None, None]:
        """Yield subscriber documents for a product one by one with."""
        obj_id = self.validate_obj_id(product_id, "Product")

        try:
            cursor = self.subscribers.find({"product_id": obj_id})
            yield from self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error yielding subscribers for product {product_id}: {str(e)}")
            raise


    def find_subscriber(self, email_address: str) -> dict:
        """Find a single subscriber by email address."""
        try:
            subscriber = self.subscribers.find({"email_address": email_address})
            if not subscriber:
                raise DocNotFoundError(identifier=email_address, entity="Subscriber")
            return subscriber

        except Exception as e:
            raise


    def delete_subscriber(self, subscriber_id: str) -> bool:
        """Delete a subscriber document by its ID.
        """
        obj_id = self.validate_obj_id(subscriber_id, "Subscriber")

        try:
            result = self.subscribers.delete_one({"_id": obj_id})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Deleted subscriber {subscriber_id}")
            else:
                DocNotFoundError(identifier=subscriber_id, entity="Subscriber")
            return deleted

        except Exception as e:
            logger.error(f"Error deleting subscriber {subscriber_id}: {str(e)}")
            raise