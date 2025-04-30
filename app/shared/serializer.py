import re
from datetime import datetime

class Serializer:
    def __init__(self):
        pass

    @staticmethod
    def json_serialize_doc(document: dict) -> dict:
        """Convert MongoDB objects for JSON serialization."""
        if document is None:
            return None

        doc = document.copy()
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()

        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc


    @staticmethod
    def json_serialize_docs(documents: list[dict]) -> list[dict]:
        """Convert _id field to string for each document in a list."""
        return [Serializer.json_serialize_doc(doc) for doc in documents if doc is not None]

