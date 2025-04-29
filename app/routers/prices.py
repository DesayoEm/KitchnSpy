from fastapi import APIRouter
from app.crud.prices import PricesCrud

router = APIRouter()
prices_crud = PricesCrud()

@router.post("/")
async def log_price(product_id: str):
    return prices_crud.log_price(product_id)

@router.post("/batch")
async def log_prices(data: dict):
    return prices_crud.log_prices(data)

@router.get("/")
async def get_all_prices():
    return prices_crud.find_all_prices()

@router.get("/{product_id}/history")
async def get_price_history(product_id: str):
    return prices_crud.yield_product_price_history(product_id)

@router.delete("/{price_id}")
async def delete_price(price_id: str):
    prices_crud.delete_price(price_id)
    return {"message": "Price deleted successfully"}

@router.delete("/")
async def delete_old_prices():
    deleted = prices_crud.delete_old_price_logs()
    return {"message": f"{deleted} Prices deleted successfully"}