from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime, timezone


class SubscriberCreate(BaseModel):
    name: str
    email_address: EmailStr
    product_name: str
    product_url: str
    subscribed_on: datetime= Field(default_factory=datetime.now(timezone.utc))
