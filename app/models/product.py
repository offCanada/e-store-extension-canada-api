from enum import Enum
from pydantic import BaseModel

class NutrientValue(BaseModel):
    value: str | None = None
    level: str = "unknown"

class NutrientLevels(BaseModel):
    fat: NutrientValue
    saturated_fat: NutrientValue
    sugars: NutrientValue
    sodium: NutrientValue

class Scores(BaseModel):
    nutri_score: str = "unknown"
    eco_score: str = "unknown"
    nova_score: str = "unknown"

class MatchType(str, Enum):
    DIRECT = "direct"
    SEARCH = "search"

class Product(BaseModel):
    barcode: str
    product_id: str

    brand: str
    title: str
    image_url: str
    taxonomy: str
    size: str
    serving_size: str

    scores: Scores
    nutrient_levels: NutrientLevels

    match_type: MatchType

class ProductResponse(BaseModel):
    status: bool
    message: str
    product: Product | None = None
    error: str | None = None 