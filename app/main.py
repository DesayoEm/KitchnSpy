from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
current_dir = Path(__file__).resolve().parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)
from app.infra.log_service import logger
from app.infra.middleware import ExceptionMiddleware
from app.routers import products, prices,  subscribers


version = "v1"
app = FastAPI(
    version = version,
    title = "Kitchnspy"
)

app.add_middleware(ExceptionMiddleware)


app.include_router(products.router, prefix=f"/api/{version}/products",
                   tags=["Products"])
app.include_router(prices.router, prefix=f"/api/{version}/prices",
                   tags=["Prices"])
app.include_router(subscribers.router, prefix=f"/api/{version}/subscribers",
                   tags=["Subscribers"])



@app.get("/kitchnspy")
async def root():
    return {"message": "Welcome to KitchnSpy!"}

logger.info("Application started")