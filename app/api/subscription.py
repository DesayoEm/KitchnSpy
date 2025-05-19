from fastapi import APIRouter, Query
from app.domain.subscribers.services.subscription_service import SubscriptionService
from app.domain.subscribers.schemas import SubscriberData
from fastapi.responses import StreamingResponse
import json


router = APIRouter()
subscription_crud = SubscriptionService()

@router.post("/products/{product_id}/subscribe")
async def subscribe(product_id: str, data: SubscriberData):
    subscription_crud.add_subscriber(product_id, data)
    return {"message": "Subscribed successfully. Please check your email for confirmation."}

@router.post("/products/{product_id}/unsubscribe")
async def unsubscribe(email_address: str, product_id: str):
    subscription_crud.remove_subscriber(email_address, product_id)
    return {"message": "Unsubscribed successfully. You will no longer receive updates."}


@router.get("/subscribers/{email_address}")
async def get_subscriber_by_email(email_address: str):
    return subscription_crud.get_subscriber_by_email(email_address)

@router.get("/{subscriber_id}/subscribers")
async def get_product_subscribers(
    product_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    generator = subscription_crud.yield_and_paginate_product_subscribers(product_id, page, per_page)

    def stream_json_array():
        yield b"["
        first = True

        for document in generator:
            if not first:
                yield b","
            else:
                first = False
            yield json.dumps(document).encode()

        yield b"]"
    return StreamingResponse(stream_json_array(), media_type="application/json")


@router.get("/")
async def get_all_subscribers(page: int = Query(1, ge=1, description="Page number"),
                         per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    generator = subscription_crud.yield_all_subscribers(page, per_page)

    def stream_json_array():
        yield b"["
        first = True

        for document in generator:
            if not first:
                yield b","
            else:
                first = False
            yield json.dumps(document).encode()

        yield b"]"

    return StreamingResponse(stream_json_array(), media_type="application/json")


@router.delete("/subscribers/{subscriber_id}")
async def delete_subscriber(subscriber_id: str):
    subscription_crud.delete_subscriber(subscriber_id)
    return {"message": "Subscriber deleted successfully"}