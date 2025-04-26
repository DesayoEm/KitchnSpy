from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone

class SubscriberData(BaseModel):
    """Schema for subscriber data associated with a product."""
    name: str
    email_address: EmailStr
    product_id: str
    product_name: str
    product_url: str
    subscribed_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
