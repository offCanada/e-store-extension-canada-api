from itertools import product
import random

from app.models.product import MatchType, NutrientLevels, NutrientValue, Product, Scores
from app.models.product_search_params import ProductSearchParams


class ProductService:
    def __init__(self, con):
        self.con = con

    def lookup_by_ids(self, product_id: str | None, code: str | None) -> dict | None:
        """Direct lookup based on product id or barcode or both."""
        conditions = []
        params = []

        if product_id:
            conditions.append("external_id = ?")
            params.append(product_id)
        if code:
            conditions.append("upc = ?")
            params.append(code)

        if not conditions:
            return None

        query = f"SELECT * FROM product_merged WHERE {' AND '.join(conditions)} LIMIT 1"
        cursor = self.con.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    def search_by_query(self, search_query: str, limit: int = 10) -> list[dict]:
        """Fallback fuzzy/text search."""
        cursor = self.con.execute(
            "SELECT * FROM product_merged WHERE title ILIKE ? OR brand ILIKE ? LIMIT ?",
            [f"%{search_query}%", f"%{search_query}%", limit],
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def find(self, params: ProductSearchParams) -> Product | None:
        """Orchestrates: try exact lookup first, fall back to search."""
        if params.product_id or params.code:
            product = self.lookup_by_ids(params.product_id, params.code)
            if product is not None:
                return self.build_product(product, MatchType.DIRECT)

        # if params.search_query:
        #     return self.search_by_query(params.search_query)

        return None

    def build_product(self, row: dict, match_type: MatchType) -> Product:
        """Assembly — maps raw + computed data into the response model."""

        return Product(
            barcode=row["upc"],
            product_id=row["external_id"],
            brand=row["brand"],
            title=row["core_title"],
            image_url=row["image_url"],
            taxonomy=row["reference_db_taxonomy"].title(),
            size=row["size"],
            serving_size=row["serving_size"],
            scores=self.compute_scores(row),
            nutrient_levels=self.compute_nutrient_levels(row),
            match_type=match_type
        )

    def compute_scores(self, row: dict) -> Scores:
        """Compute product scores from raw row data."""
        grades = ['a', 'b', 'c', 'd', 'e', 'unknown']
        return Scores(
            nutri_score=self.compute_nutri_score(row["nutri_score_points"]),
            eco_score=grades[random.randint(0, 4)],
            nova_score=str(random.randint(1,4)),
        )

    def compute_nutri_score(self, points: float | None) -> str:
        if points is None or not isinstance(points, (int, float)):
            return "unknown"
        if points <= 0:
            return "a"
        if points <= 2:
            return "b"
        if points <= 10:
            return "c"
        if points <= 18:
            return "d"
        return "e"

    def compute_nutrient_levels(self, row: dict) -> NutrientLevels:
        """Compute nutrient levels from raw row data."""
        return NutrientLevels(
            fat=NutrientValue(
                value=self.format_nutrient_value(row["fat_per_100g"], 'g'),
                level="low"
            ),
            saturated_fat=NutrientValue(
                value=self.format_nutrient_value(row["saturated_fat_per_100g"], 'g'),
                level="moderate"
            ),
            sugars=NutrientValue(
                value=self.format_nutrient_value(row["sugars_per_100g"], 'g'),
                level="high"
            ),
            sodium=NutrientValue(
                value=self.format_nutrient_value(row["sodium_per_100g"], 'mg'),
                level="unknown"
            )
        )

    def format_nutrient_value(self, value: float | None, unit: str) -> str | None:
        if value is None:
            return None
        return f"{value:.2f}{unit}/100g"