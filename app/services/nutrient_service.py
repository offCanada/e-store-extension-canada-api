import re

from app.models.product import NutrientLevels, NutrientValue


class NutrientService:
    """Computes per-nutrient levels (low / moderate / high) from Daily Value percentages.

    Calculation rule
    -----------------
    Values in ``product_merged`` are stored per 100 g of product. They are scaled
    to an actual serving before comparison against Health Canada reference daily
    values (2,000 kcal diet), matching the official label %DV methodology:

        serving_amount = amount_per_100g * serving_grams / 100
        %DV            = (serving_amount / daily_value) * 100

    ``serving_size`` strings are parsed to grams; ``kg``, ``mg``, ``l`` and ``ml``
    are converted (``ml`` assumes ~1 g/ml density). When the serving size is
    missing or unparseable, classification falls back to the raw per-100g amount.

    Level thresholds (per %DV):
        low       <= 5%
        moderate  > 5% and <= 15%
        high      > 15%

    A missing nutrient yields ``level="unknown"``.
    """

    DAILY_VALUES = {"fat": 75.0, "saturated_fat": 20.0, "sugars": 100.0, "sodium": 2300.0}
    UNITS = {"fat": "g", "saturated_fat": "g", "sugars": "g", "sodium": "mg"}

    _SERVING_RE = re.compile(r"^([\d.]+)\s*(kg|mg|ml|l|g)$", re.IGNORECASE)
    _TO_GRAMS = {"g": 1.0, "kg": 1000.0, "mg": 0.001, "ml": 1.0, "l": 1000.0}

    def compute_nutrient_levels(self, product: dict) -> NutrientLevels:
        """Build a :class:`NutrientLevels` from a raw product dict.

        Reads the ``*_per_100g`` columns; each is passed to :meth:`_build_nutrient`
        along with the parsed serving size.
        """
        serving_grams = self._parse_serving_grams(product.get("serving_size"))
        return NutrientLevels(
            fat=self._build_nutrient(product.get("fat_per_100g"), "fat", serving_grams),
            saturated_fat=self._build_nutrient(product.get("saturated_fat_per_100g"), "saturated_fat", serving_grams),
            sugars=self._build_nutrient(product.get("sugars_per_100g"), "sugars", serving_grams),
            sodium=self._build_nutrient(product.get("sodium_per_100g"), "sodium", serving_grams),
        )

    def _parse_serving_grams(self, serving_size) -> float | None:
        """Parse a ``serving_size`` string (e.g. ``"30 g"``, ``"250 ml"``) into grams.

        Returns ``None`` when the value is missing or cannot be parsed.
        """
        if serving_size is None:
            return None
        match = self._SERVING_RE.match(str(serving_size).strip())
        if match is None:
            return None
        return float(match.group(1)) * self._TO_GRAMS[match.group(2).lower()]

    def _build_nutrient(self, value: float | None, nutrient: str, serving_grams: float | None) -> NutrientValue:
        """Build a single :class:`NutrientValue`.

        The amount is scaled to the serving size when available (basis
        ``"/serving"``), otherwise used as-is (basis ``"/100g"``), formatted as
        ``"<amount>.XX<unit>/<basis>"`` and classified into a level via
        :meth:`_classify`. Returns ``value=None, level="unknown"`` when the raw
        value is missing.
        """
        if value is None:
            return NutrientValue(value=None, level="unknown")
        if serving_grams is not None:
            amount = value * serving_grams / 100
            basis = "serving"
        else:
            amount = value
            basis = "100g"
        percent_dv = (amount / self.DAILY_VALUES[nutrient]) * 100
        return NutrientValue(
            value=f"{amount:.2f}{self.UNITS[nutrient]}/{basis}",
            level=self._classify(percent_dv),
        )

    def _classify(self, percent_dv: float) -> str:
        """Map a %DV to a level: <=5% low, <=15% moderate, otherwise high."""
        if percent_dv <= 5:
            return "low"
        if percent_dv <= 15:
            return "moderate"
        return "high"
