from app.infra.db.adapters.shared_imports import *
from app.infra.db.adapters.base_adapter import BaseAdapter

load_dotenv()

class SubscriberAdapter(BaseAdapter):

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

    def yield_product_subscribers(self, product_id: str) -> Generator[
        Dict, None, None]:
        """Yield subscriber documents for a specific product one at a time"""
        try:
            cursor = self.subscribers.find({"product_id": product_id})
            yield from self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error yielding subscribers for product {product_id}: {str(e)}")
            raise


    def yield_and_paginate_product_subscribers(
            self, product_id: str, page: int = 1, per_page: int = 20
    ) -> Generator[Dict, None, None]:
        """Yield paginated subscriber documents for a specific product."""
        try:
            skip = (page - 1) * per_page if page > 0 else 0

            cursor = self.subscribers.find({"product_id": product_id})
            cursor.sort("subscribed_on", pymongo.ASCENDING) \
                .skip(skip).limit(per_page)
            yield from self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error yielding all subscribers: {str(e)}")
            raise


    def yield_and_paginate_all_subscribers(self, page: int = 1, per_page: int = 20) -> Generator[Dict, None, None]:
        """Yield all subscriber documents across all products, paginated."""
        try:
            skip = (page - 1) * per_page if page > 0 else 0

            cursor = self.subscribers.find({}) \
                .sort("subscribed_on", pymongo.ASCENDING) \
                .skip(skip).limit(per_page)

            yield from self.yield_documents(cursor)

        except Exception as e:
            logger.error(f"Error yielding all subscribers: {str(e)}")
            raise


    def find_subscriber_by_email(self, email_address: str) -> list[dict]:
        """Retrieve a single subscriber by email and product ID."""
        try:
            subscriber = self.subscribers.find({"email_address": email_address})
            logger.info(f"Finding by {email_address}. type{type(email_address)}")
            if not subscriber:
                raise DocNotFoundError(identifier=email_address, entity="Subscriber")
            return list(subscriber)
        except Exception:
            raise

    def find_product_subscriber(self, email_address: str, product_id: str) -> dict:
        """Retrieve a single subscriber by email and product ID."""
        return self.subscribers.find_one(
            {"email_address": email_address.lower(), "product_id": product_id}
        )


    def delete_subscriber(self, subscriber_id: str) -> bool:
        """Delete a subscriber by their ID."""
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