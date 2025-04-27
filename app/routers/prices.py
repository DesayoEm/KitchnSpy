from fastapi import APIRouter
from app.crud.prices import PricesCrud

router = APIRouter()
prices_crud = PricesCrud()

@router.get("/")
async def get_all_prices():
    return prices_crud.find_all_prices()

@router.get("/{product_id}/history")
async def get_price_history(product_id: str):
    return prices_crud.get_price_history(product_id)

@router.delete("/{price_id}")
async def delete_price(price_id: str):
    return prices_crud.delete_price(price_id)
