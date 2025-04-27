class Utils:
    def __init__(self):
        pass


    @staticmethod
    def convert_objectid_to_str(document: dict) -> dict:
        """Convert MongoDB ObjectId fields to strings for JSON serialization."""
        if document is None:
            return None

        doc = document.copy()
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc


    @staticmethod
    def convert_objectid_in_list(documents: list[dict]) -> list[dict]:
        """Convert _id field to string for each document in a list."""
        return [Utils.convert_objectid_to_str(doc) for doc in documents if doc is not None]
