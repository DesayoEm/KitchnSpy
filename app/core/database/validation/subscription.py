from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime, timezone

class SubscriberData(BaseModel):
    """Schema for subscriber data associated with a product."""
    name: str
    email_address: EmailStr
    subscribed_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "name": "moria",
                "email_address": "Labaekaadesayo@gmail.com",

            }
        }
    )

class UnSubscribeData(BaseModel):
        """Schema for subscriber data associated with a product."""
        name: str
        email_address: EmailStr


