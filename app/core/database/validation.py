from pydantic import BaseModel, field_validator, HttpUrl
from datetime import datetime
import re

class ProductData(BaseModel):
    name: str|None
    url: str|None
    price: str|None
    is_available: bool|None
    img_url: str|None
    date_checked: datetime
    status: str


    @field_validator('price')
    def validate_price_format(cls, value):
        if not value.strip().startswith("£"):
            raise ValueError("Price must start with '£'")
        matches = re.findall(r'£\s*(\d+(?:\.\d{2})?)', value)

        if not matches:
            return value

        numeric_prices = [float(p) for p in matches]
        highest_price = max(numeric_prices)

        return f"£ {highest_price:.2f}"


