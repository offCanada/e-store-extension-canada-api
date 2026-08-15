import random

from app.models.product import MatchType, NutrientLevels, Product, Scores
from app.models.product_search_params import ProductSearchParams
from app.services.nutrient_service import NutrientService


class ProductService:
    """Handles product lookup and assembly into the response model.

    Orchestrates exact lookup by barcode/UPC or product id, then maps the raw
    database row into a :class:`Product`, delegating score and nutrient-level
    computation to dedicated services.
    """

    def __init__(self, con):
        self.con = con

    def lookup_by_ids(self, product_id: str | None, code: str | None) -> dict | None:
        """Direct lookup based on product id (``external_id``) or barcode (``upc``) or both.

        Returns the first matching raw product details as a dict, or ``None`` if no
        match is found. Both identifiers may be provided; they are combined with ``AND``.
        """
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
        product = cursor.fetchone()
        if product is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, product))

    def find(self, params: ProductSearchParams) -> Product | None:
        """Orchestrates: try exact lookup first, fall back to search."""
        if params.product_id or params.code:
            product = self.lookup_by_ids(params.product_id, params.code)
            if product is not None:
                return self.build_product(product, MatchType.DIRECT)

        return None

    def build_product(self, product: dict, match_type: MatchType) -> Product:
        """Assembly — maps raw + computed data into the response model.

        Fields like ``scores`` and ``nutrient_levels`` are computed by delegating to
        :meth:`compute_scores` and :meth:`compute_nutrient_levels`.
        """

        return Product(
            barcode=product["upc"],
            product_id=product["external_id"],
            brand=product["brand"],
            title=product["core_title"],
            image_url=product["image_url"],
            taxonomy=product["reference_db_taxonomy"].title(),
            size=product["size"],
            serving_size=product["serving_size"],
            scores=self.compute_scores(product),
            nutrient_levels=self.compute_nutrient_levels(product),
            match_type=match_type
        )

    def compute_scores(self, product: dict) -> Scores:
        """Compute product scores from raw product data.

        ``nutri_score`` is derived from ``nutri_score_points`` via
        :meth:`compute_nutri_score`. ``eco_score`` and ``nova_score`` are placeholders
        (random dummies) until their real calculators are implemented.
        """
        grades = ['a', 'b', 'c', 'd', 'e', 'unknown']
        return Scores(
            nutri_score=self.compute_nutri_score(product["nutri_score_points"]),
            eco_score=grades[random.randint(0, 4)],
            nova_score=str(random.randint(1,4)),
        )

    def compute_nutri_score(self, points: float | None) -> str:
        """Map raw Nutri-Score points to a letter grade (``a``-``e``).

        Thresholds:
            a: points <= 0
            b: points 1-2
            c: points 3-10
            d: points 11-18
            e: points > 18

        A ``None`` or non-numeric value yields ``"unknown"``.
        """
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

    def compute_nutrient_levels(self, product: dict) -> NutrientLevels:
        """Compute nutrient levels from raw product data."""
        return NutrientService().compute_nutrient_levels(product)