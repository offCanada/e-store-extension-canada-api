from fastapi import APIRouter
from app.routers import products

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(products.router, prefix="/products", tags=["products"])