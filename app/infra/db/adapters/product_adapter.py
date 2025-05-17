from app.infra.db.adapters.shared_imports import *
from app.infra.db.adapters.base_adapter import BaseAdapter

load_dotenv()

class ProductAdapter(BaseAdapter):

    def compile_product_ids(self) -> List[str]:
        """ Retrieve all product IDs from the database."""
        product_ids = [str(doc["_id"]) for doc in self.products.find({}, {"_id": 1})]
        return product_ids


    def insert_product(self, data: dict) -> InsertOneResult:
        """Insert a single product document into the database."""
        try:
            result = self.products.insert_one(data)
            logger.info(f"Inserted product with ID: {result.inserted_id}")
            return result

        except DuplicateKeyError:
            raise DuplicateEntityError(entry=data["url"], entity="Product")

        except Exception as e:
            logger.error(f"Failed to insert product: {str(e)}")
            raise


    def find_product(self, product_id: str) -> dict:
        """Retrieve a product document by its ID."""
        return self.find_by_id(self.products, product_id, "Product")


    def find_product_by_url(self, url: str) -> dict:
        """Retrieve a product document by its URL."""
        prod =  self.products.find_one({"url": url})
        if not prod:
            raise DocNotFoundError(identifier=url, entity="Product")
        return prod


    def find_products_paginated(self, page: int = 1) -> List[dict]:
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
        """Search products by name using a regex query and yield paginated results."""
        search_term = search_term.strip()
        if len(search_term) == 0:
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

            first_doc = next(cursor, None)
            if not first_doc:
                raise DocsNotFoundError(entities="Products", page=page)

            yield from self.yield_documents(itertools.chain([first_doc], cursor))

        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            raise


    def replace_product(self, product_id: str, new_document: dict) -> dict:
        """Replace the entire product document by ID."""
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


    def bulk_replace_products(self, operations: list[dict]) -> int:
        """Perform a bulk upsert operation on product documents"""
        if not operations:
            return 0

        mongo_ops = [
            ReplaceOne(op["filter"], op["replacement"])
            for op in operations
        ]
        result = self.products.bulk_write(mongo_ops, ordered=False)
        logger.info(f"Bulk updated {result.modified_count} products")
        return result.modified_count


    def delete_product(self, product_id: str) -> None:
        """ Delete a product document from the database by its ID."""
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


