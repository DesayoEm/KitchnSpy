from fastapi import APIRouter
from app.core.database.validation.product import ProductCreate, ProductsCreateBatch
from app.crud.products import ProductCrud

router = APIRouter()
products_crud = ProductCrud()

@router.post("/")
async def add_product(data: ProductCreate):
    return products_crud.add_product(data)

@router.post("/batch")
async def add_products(data: ProductsCreateBatch):
    return products_crud.add_products(data)

@router.get("/")
async def get_all_products():
    return products_crud.find_all_products()

@router.get("/{product_id}")
async def get_product(product_id: str):
    return products_crud.find_product(product_id)

@router.put("/{product_id}")
async def update_product(product_id: str):
    return products_crud.update_product(product_id)

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    return products_crud.delete_product(product_id)
