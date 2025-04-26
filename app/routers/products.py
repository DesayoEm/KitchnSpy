from fastapi import APIRouter

from app.crud.prices import PricesCrud
from app.crud.products import ProductCrud
from app.crud.subscription import SubscriptionCrud

router = APIRouter()
products_crud = ProductCrud()
prices_crud = PricesCrud()
subscription_crud = SubscriptionCrud()


@router.post("/")
async def add_product(url: str):
    return products_crud.add_product(url)

@router.post("/")
async def get_all_products():
    return products_crud.find_products()


@router.get("/{product_id}")
async def get_product(product_id):
    return products_crud.find_product(product_id)

@router.put("/{product_id}")
async def update_product(product_id):
    return products_crud.find_product(product_id)


@router.get("/{product_id}/price_history")
async def get_price_history(product_id):
    return prices_crud.get_price_history(product_id)

@router.post("/{product_id}/subscribe")
async def subscribe_to_notifications(data: dict):
    subscription_crud.add_subscriber(data)
    return "sUCCESSFUL"


@router.post("/{product_id}/unsubscribe")
async def unsubscribe_from_notifications(data: dict):
    subscription_crud.remove_subscriber(data)
    return "sUCCESSFUL"


@router.delete("/{product_id}")
async def delete_product(product_id):
    return products_crud.delete_product(product_id)


@router.post("/")
async def add_product(url: str):
    return products_crud.add_product(url)

@router.post("/")
async def get_all_prices():
    return prices_crud.get_all_prices()

@router.delete("/prices")
async def delete_price(price_id):
    return prices_crud.delete_price(price_id)
