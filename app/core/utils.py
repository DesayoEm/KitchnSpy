import re
from datetime import datetime

class Utils:
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
        return [Utils.json_serialize_doc(doc) for doc in documents if doc is not None]

    @staticmethod
    def parse_price(price_str: str) -> float:
        return float(price_str.replace("£", "").replace(",", ""))

    @staticmethod
    def validate_price_format(value: str) -> str:
        """Validate that the price starts with '£' and format it."""

        if not value.strip().startswith("£"):
            raise ValueError("Price must start with '£'")

        matches = re.findall(r'£\s*(\d+(?:\.\d{2})?)', value)
        if not matches:
            return value

        numeric_prices = [float(p) for p in matches]
        highest_price = max(numeric_prices)

        return f"£ {highest_price:.2f}"
