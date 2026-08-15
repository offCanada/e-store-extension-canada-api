import asyncio
import json
from types import SimpleNamespace
from typing import cast

from fastapi import HTTPException
from limits import parse
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.wrappers import Limit
from starlette.requests import Request

from app.configs.limiter import limiter
from app.exceptions import handlers
from app.exceptions.errors import ProductNotFoundError


def _loads(response) -> dict:
    return json.loads(bytes(response.body))


class TestErrorResponse:
    def test_envelope_shape(self):
        response = handlers.error_response(422, "bad", error="detail")
        assert response.status_code == 422
        assert _loads(response) == {"status": False, "message": "bad", "error": "detail"}

    def test_no_product_key(self):
        response = handlers.error_response(500, "oops")
        assert "product" not in _loads(response)


class TestProductNotFoundHandler:
    def test_body_includes_product_none(self):
        response = asyncio.run(
            handlers.product_not_found_handler(cast(Request, None), ProductNotFoundError())
        )
        assert response.status_code == 404
        assert _loads(response) == {
            "status": False,
            "message": "product not found",
            "product": None,
            "error": "product not found",
        }


class TestValidationHandler:
    def test_returns_422_envelope(self):
        error = ValidationError.from_exception_data("ProductSearchParams", [])
        response = asyncio.run(
            handlers.validation_exception_handler(cast(Request, None), error)
        )
        assert response.status_code == 422
        body = _loads(response)
        assert body["status"] is False
        assert body["message"] == "invalid request parameters"
        assert "product" not in body


class TestHttpExceptionHandler:
    def test_string_detail(self):
        response = asyncio.run(
            handlers.http_exception_handler(
                cast(Request, None), HTTPException(status_code=400, detail="bad request")
            )
        )
        assert response.status_code == 400
        body = _loads(response)
        assert body["status"] is False
        assert body["message"] == "bad request"
        assert "product" not in body


class TestUnhandledHandler:
    def test_returns_500_envelope(self, monkeypatch):
        monkeypatch.setattr(handlers.logger, "exception", lambda *args, **kwargs: None)
        request = cast(Request, SimpleNamespace(url="http://test"))
        response = asyncio.run(handlers.unhandled_exception_handler(request, RuntimeError("boom")))
        assert response.status_code == 500
        body = _loads(response)
        assert body["status"] is False
        assert body["message"] == "internal server error"
        assert "product" not in body


class TestRateLimitHandler:
    def test_returns_429_envelope(self):
        limiter.enabled = False
        request = cast(
            Request,
            SimpleNamespace(
                app=SimpleNamespace(state=SimpleNamespace(limiter=limiter)),
                state=SimpleNamespace(view_rate_limit=None),
            ),
        )
        response = asyncio.run(
            handlers.rate_limit_exceeded_handler(
                request,
                RateLimitExceeded(
                    Limit(parse("30/minute"), get_remote_address, None, False, None, None, None, 1, True)
                ),
            )
        )
        assert response.status_code == 429
        body = _loads(response)
        assert body["status"] is False
        assert body["message"] == "rate limit exceeded"
        assert "product" not in body