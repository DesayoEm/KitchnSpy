from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
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

    @field_validator('email_address')
    def validate_price_format(cls, value: str) -> str:
        """return email address as a lowercase str."""

        return value.lower()


class UnSubscribeData(BaseModel):
        """Schema for subscriber data associated with a product."""
        name: str
        email_address: EmailStr


