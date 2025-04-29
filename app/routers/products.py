from fastapi import APIRouter
from app.core.database.validation.product import ProductCreate, ProductsCreateBatch, ProductsUpdateBatch
from app.crud.products import ProductCrud

router = APIRouter()
products_crud = ProductCrud()

@router.post("/")
async def add_product(data: ProductCreate):
    return products_crud.add_product(data)

@router.post("/batch")
async def add_products(data: ProductsCreateBatch):
    return products_crud.add_products(data)

@router.get("/search")
async def search_products(term):
    return products_crud.search_products_by_name(term)

@router.get("/{product_id}")
async def get_product(product_id: str):
    return products_crud.find_product(product_id)

@router.get("/")
async def get_all_products():
    return products_crud.find_all_products()

@router.put("/{product_id}")
async def update_product(product_id: str):
    return products_crud.update_or_replace_product(product_id)

@router.put("/")
async def update_products(data: ProductsUpdateBatch):
    return products_crud.bulk_update_products(data)

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    products_crud.delete_product(product_id)
    return {"message": "Product deleted successfully"}
