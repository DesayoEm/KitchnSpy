from itertools import product

from fastapi import Depends, APIRouter

from app.crud.scrape import ProductCrud

router = APIRouter()
products_crud = ProductCrud()


@router.get("/products")
async def get_all_products():
    return products_crud.g
