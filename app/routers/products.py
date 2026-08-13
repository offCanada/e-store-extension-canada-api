import logging

from fastapi import APIRouter, Request, Depends

from app.configs.db import get_db
from app.configs.limiter import limiter
from app.exceptions import ProductNotFoundError
from app.models.product import ProductResponse
from app.models.product_search_params import ProductSearchParams
from app.services.product_service import ProductService

logger = logging.getLogger("uvicorn.error")

router = APIRouter()

def get_product_service(con=Depends(get_db)) -> ProductService:
    return ProductService(con)

@router.get("/search", response_model=ProductResponse)
@limiter.limit("30/minute")
def get_product(request: Request, params: ProductSearchParams = Depends(), service: ProductService = Depends(get_product_service)):
    product = service.find(params)

    if not product:
        raise ProductNotFoundError()

    logger.info("GET %s - params=%s", request.url, params)

    return ProductResponse(
        status=True,
        message="product found",
        product=product,
    )