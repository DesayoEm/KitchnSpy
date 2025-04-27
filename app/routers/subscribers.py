from fastapi import APIRouter
from app.crud.subscribers import SubscriberCrud
from app.core.database.validation.subscription import SubscriberData

router = APIRouter()
subscription_crud = SubscriberCrud()

@router.post("/{product_id}/subscribe")
async def subscribe_to_notifications(product_id: str, data: SubscriberData):
    subscription_crud.add_subscriber(product_id, data)
    return {"message": "Subscribed successfully. Please check your email for confirmation."}


@router.post("/{product_id}/unsubscribe")
async def unsubscribe_from_notifications(product_id: str, email_address: str):
    subscription_crud.remove_subscriber(product_id, email_address)
    return {"message": "Unsubscribed successfully. You will no longer receive updates."}