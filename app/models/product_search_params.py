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

    @model_validator(mode="after")
    def check_at_least_one(self):
        if not any([self.product_id, self.code, self.search_query]):
            raise ValueError("Provide at least one of product_id, code, or search_query")
        return self