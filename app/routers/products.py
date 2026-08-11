from fastapi import APIRouter, Request, HTTPException

from app.configs.limiter import limiter

router = APIRouter()

# @router.get("/{barcode}", response_model=Product)
# @limiter.limit("30/minute")