import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded

from app.exceptions.errors import ProductNotFoundError

logger = logging.getLogger("uvicorn.error")


def error_response(status_code: int, message: str, error: str | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": False,
            "message": message,
            "error": error,
        },
    )

async def product_not_found_handler(request: Request, exc: ProductNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "status": False,
            "message": exc.message,
            "product": None,
            "error": exc.message,
        },
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    return error_response(status_code=422, message="invalid request parameters", error=str(exc.errors()))


async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return error_response(status_code=exc.status_code, message=detail, error=detail)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    response = error_response(status_code=429, message="rate limit exceeded", error=exc.detail)
    return request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s", request.url)
    return error_response(status_code=500, message="internal server error", error="internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ProductNotFoundError, product_not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, validation_exception_handler)    # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)            # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)