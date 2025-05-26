from app.infra.db.adapters.shared_imports import *
load_dotenv()


class BaseAdapter:
    """
    Base MongoDB adapter for initializing collections and providing shared utilities.
    """

    def __init__(self):
        """Establish MongoDB connection and initialize core collections."""

        uri = os.getenv('DB_URI')
        if not uri:
            raise URIConnectionError()
        try:
            client = MongoClient(uri)
            db = client['kitchnspy']
            self.products = db["products"]
            self.price_logs = db["price_log"]
            self.subscribers = db["subscribers"]
            self.tasks = db["task_audit"]
            self.celery_results = db["celery_results"]
            self.serializer = Serializer()
            self.ensure_indexes()

            logger.info("MongoDB connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise


    def ensure_indexes(self) -> None:
        """Create indexes on collections"""
        self.products.create_index([("product_name", pymongo.ASCENDING)])

        self.products.create_index(
            [("url", pymongo.ASCENDING)],
            unique=True
        )

        self.price_logs.create_index([
            ("product_id", pymongo.ASCENDING),
            ("date_checked", pymongo.ASCENDING)
        ])

        self.subscribers.create_index([
            ("email_address", pymongo.ASCENDING),
            ("product_id", pymongo.ASCENDING)
        ], unique=True)


    @staticmethod
    def validate_obj_id(id_str: str, entity_name: str = "Document") -> ObjectId:
        """Convert a string ID to an ObjectId"""
        try:
            return ObjectId(id_str)
        except InvalidId as e:
            raise InvalidIdError(entity=entity_name, detail=str(e))


    def find_by_id(self, collection, doc_id: str, entity_name: str) -> dict:
        """Retrieve a document by ID from the specified collection."""
        obj_id = self.validate_obj_id(doc_id, entity_name)
        document = collection.find_one({"_id": obj_id})
        if not document:
            raise DocNotFoundError(identifier=doc_id, entity=entity_name)

        return document


    def yield_documents(self, cursor) -> Generator[Dict, None, None]:
        """Yield documents from a MongoDB cursor one at a time, serialized as dictionaries"""
        for document in cursor:
            yield self.serializer.json_serialize_doc(document)



    def paginate_results(self, cursor, per_page, page: int = 1) -> List[Dict]:
        """
        Return a paginated list of documents from a cursor.
        Args:
            cursor: MongoDB cursor object.
            page: Page number (1-based).
            per_page: Number of documents per page.

        Returns:
            A list of document dictionaries.
        """
        skip = (page - 1) * per_page if page > 0 else 0
        return list(cursor.skip(skip).limit(per_page))
