from fastapi import APIRouter, Query, HTTPException
from app.crud.prices import PricesCrud
from fastapi.responses import StreamingResponse
import json




router = APIRouter()
prices_crud = PricesCrud()


@router.post("/batch")
async def log_prices():
    return prices_crud.log_prices()


@router.post("/")
async def log_price(product_id: str):
    return prices_crud.log_price(product_id)


@router.get("/{product_id}/history")
async def get_price_history(
    product_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    generator = prices_crud.yield_product_price_history(product_id, page, per_page)

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
async def get_all_prices(page: int = Query(1, ge=1, description="Page number"),
                         per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    generator = prices_crud.yield_all_prices(page, per_page)

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


@router.delete("/{price_id}")
async def delete_price(price_id: str):
    prices_crud.delete_price(price_id)
    return {"message": "Price deleted successfully"}

@router.delete("/")
async def delete_old_prices():
    deleted = prices_crud.delete_old_price_logs()
    return {"message": f"{deleted} Prices deleted successfully"}