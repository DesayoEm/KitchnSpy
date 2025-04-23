from pydantic import BaseModel, field_validator
from datetime import datetime

class ProductData(BaseModel):
    name: str|None
    url: str|None
    price: str|None
    availability: int|None
    img_url: str|None
    date_checked: datetime
    status: str

    @field_validator('price')
    def validate_price_format(cls, value):
        if not value.strip().startswith("£"):
            raise ValueError("Price must start with '£'")
        return value.strip()