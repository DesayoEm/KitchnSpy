from pydantic import BaseModel, field_validator, ConfigDict
from typing import List
from datetime import datetime
import re

class ProductCreate(BaseModel):
    """
    Schema for creating a single product.
    """
    name: str
    url: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "name": "Glass Mixing bowl",
                "url": "https://www.kitchenaid.co.uk/mixing-bowls/859711694400/glass-mixing-bowl-4-7-l-5ksm5gb-transparent"
            }}
    )


class ProductsCreateBatch(BaseModel):
    """
    Schema for batch creating multiple products.
    """
    products: List[ProductCreate]

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "products": [
                    {
                        "name": "Evergreen Artisan",
                        "url": "https://www.kitchenaid.co.uk/mixers/medium/859711664810/mixer-design-series-4-7l-evergreen-artisan-5ksm180ws-evergreen"
                    },
                    {
                        "name": "Classic White",
                        "url": "https://www.kitchenaid.co.uk/mixers/medium/859700415030/mixer-tilt-head-4-3l-classic-5k45ss-white"
                    }
                ]
            }
        }
    )

class ProductsUpdateBatch(ProductsCreateBatch):
    """
    Schema for batch updating multiple products.
    """


class ProductData(ProductCreate):
    """Schema for representing product price data over time."""
    name: str | None
    product_name: str | None
    img_url: str | None
    is_available: bool | None
    date_checked: datetime
    price: str | None
    status: str


    @field_validator('price')
    def validate_price_format(cls, value: str) -> str:
        """Validate that the price starts with '£' and format it."""

        if not value.strip().startswith("£"):
            raise ValueError("Price must start with '£'")

        matches = re.findall(r'£\s*(\d+(?:\.\d{2})?)', value)
        if not matches:
            return value

        numeric_prices = [float(p) for p in matches]
        highest_price = max(numeric_prices)

        return f"£ {highest_price:.2f}"


class ProductResponse(BaseModel):
    """Schema for returning product data to the client."""
    name: str | None
    url: str | None
    price: str | None
    is_available: bool | None
    img_url: str | None
    date_checked: datetime
    status: str



