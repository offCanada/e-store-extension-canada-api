from typing import Annotated
from fastapi import Query
from pydantic import BaseModel, field_validator, model_validator

class ProductSearchParams(BaseModel):
    product_id: Annotated[str | None, Query()] = None
    code: Annotated[str | None, Query()] = None
    name: Annotated[str | None, Query()] = None
    brand: Annotated[str | None, Query()] = None
    quantity: Annotated[str | None, Query()] = None
    category: Annotated[str | None, Query()] = None
    search_query: Annotated[str | None, Query()] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.isdigit():
                raise ValueError("code must contain only digits")
            if len(v) < 6 or len(v) > 14:
                raise ValueError("code must be valid UPC")
        return v

    @field_validator("search_query")
    @classmethod
    def validate_search_query(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 250:
                raise ValueError("search_query too long (max 250 characters)")
        return v

    @model_validator(mode="before")
    @classmethod
    def normalize_blank_values(cls, data):
        if isinstance(data, dict):
            return {
                key: (None if isinstance(value, str) and not value.strip() else value)
                for key, value in data.items()
            }
        return data

    @model_validator(mode="after")
    def require_search_key(self):
        if not (self.product_id or self.code):
            raise ValueError("Provide at least one of product_id or code")
        return self