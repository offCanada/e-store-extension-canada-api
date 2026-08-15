from app.models.product import NutrientLevels, NutrientValue


class NutrientService:
    """Computes per-nutrient levels (low / moderate / high) from Daily Value percentages.

    Calculation rule
    -----------------
    Values in ``product_merged`` are stored per 100 g of product. The percent of the
    Daily Value (%DV) is computed on that 100 g basis:

        %DV = (nutrient_amount_per_100g / reference_daily_value) * 100

    Reference daily values follow Health Canada guidance for a 2,000 kcal diet
    (``DAILY_VALUES``). This is a *nutrient-density* indicator; it is an
    approximation of the label %DV, which is officially based on serving size.

    Level thresholds (per %DV):
        low       <= 5%
        moderate  > 5% and <= 15%
        high      > 15%

    A missing value yields ``level="unknown"``.
    """

    DAILY_VALUES = {"fat": 75.0, "saturated_fat": 20.0, "sugars": 100.0, "sodium": 2300.0}
    UNITS = {"fat": "g", "saturated_fat": "g", "sugars": "g", "sodium": "mg"}

    def compute_nutrient_levels(self, product: dict) -> NutrientLevels:
        """Build a :class:`NutrientLevels` from a raw product dict.

        Reads the ``*_per_100g`` columns; each is passed to :meth:`_build_nutrient`.
        """
        return NutrientLevels(
            fat=self._build_nutrient(product.get("fat_per_100g"), "fat"),
            saturated_fat=self._build_nutrient(product.get("saturated_fat_per_100g"), "saturated_fat"),
            sugars=self._build_nutrient(product.get("sugars_per_100g"), "sugars"),
            sodium=self._build_nutrient(product.get("sodium_per_100g"), "sodium"),
        )

    def _build_nutrient(self, value: float | None, nutrient: str) -> NutrientValue:
        """Build a single :class:`NutrientValue` from a raw amount.

        The amount is formatted as ``"<value>.XX<unit>/100g"`` and classified into a
        level via :meth:`_classify`. Returns ``value=None, level="unknown"`` when the
        raw value is missing.
        """
        if value is None:
            return NutrientValue(value=None, level="unknown")
        percent_dv = (value / self.DAILY_VALUES[nutrient]) * 100
        return NutrientValue(
            value=self._format_value(value, self.UNITS[nutrient]),
            level=self._classify(percent_dv),
        )

    def _classify(self, percent_dv: float) -> str:
        """Map a %DV to a level: <=5% low, <=15% moderate, otherwise high."""
        if percent_dv <= 5:
            return "low"
        if percent_dv <= 15:
            return "moderate"
        return "high"

    def _format_value(self, value: float, unit: str) -> str:
        """Format a nutrient amount rounded to 2 decimals with its unit and basis."""
        return f"{value:.2f}{unit}/100g"