from fastapi import FastAPI
from app.infra.log_service import logger
from app.infra.middleware import ExceptionMiddleware


version = "v1"
app = FastAPI(
    version = version,
    title = "Kitchnspy"
)

app.add_middleware(ExceptionMiddleware)


@app.get("/kitchnspy")
async def root():
    return {"message": "Welcome to KitchnSpy!"}

logger.info("Application started")