from pydantic import BaseModel, field_validator
from typing import List
from datetime import datetime
import re

class ProductCreate(BaseModel):
    """
    Schema for creating a single product.
    """
    name: str
    url: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Evergreen Artisan",
                "url": "https://example.com/evergreen-artisan"
            }
        }


class ProductsCreateBatch(BaseModel):
    """
    Schema for batch creating multiple products.
    """
    products: List[ProductCreate]



class ProductResponse(BaseModel):
    """Schema for returning product data to the client."""
    name: str | None
    url: str | None
    price: str | None
    is_available: bool | None
    img_url: str | None
    date_checked: datetime
    status: str

class ProductData(BaseModel):
    """Schema for representing product price data over time."""
    date_checked: datetime
    price: str | None

    @field_validator('price')
    def validate_price_format(cls, value: str) -> str:
        """Validate that the price starts with '£' and format it consistently."""

        if not value.strip().startswith("£"):
            raise ValueError("Price must start with '£'")

        matches = re.findall(r'£\s*(\d+(?:\.\d{2})?)', value)
        if not matches:
            return value

        numeric_prices = [float(p) for p in matches]
        highest_price = max(numeric_prices)

        return f"£ {highest_price:.2f}"
