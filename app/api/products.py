from fastapi import APIRouter
from app.domain.products.schema import ProductCreate, ProductsCreateBatch, ProductsUpdateBatch
from app.domain.products.services.product_service import ProductService

router = APIRouter()
products_service = ProductService()

@router.post("/")
async def add_product(data: ProductCreate):
    return products_service.add_product(data)

@router.post("/batch")
async def add_products(data: ProductsCreateBatch):
    return products_service.add_products(data)

@router.get("/search")
async def search_products(term):
    return products_service.search_products_by_name(term)

@router.get("/{product_id}")
async def get_product(product_id: str):
    return products_service.find_product(product_id)

@router.get("/")
async def get_all_products(per_page: int):
    return products_service.find_all_products(per_page)

@router.put("/{product_id}")
async def update_product(product_id: str):
    return products_service.replace_product(product_id)

@router.put("/")
async def update_products(data: ProductsUpdateBatch):
    return products_service.bulk_replace_products(data)

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    products_service.delete_product(product_id)
    return {"message": "Product deleted successfully"}
