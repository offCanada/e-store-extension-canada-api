import pytest

from app.services.nutrient_service import NutrientService


class TestComputeNutrientLevels:
    def test_typical_product(self):
        levels = NutrientService().compute_nutrient_levels(
            {"fat_per_100g": 15.0, "saturated_fat_per_100g": 3.0, "sugars_per_100g": 4.0, "sodium_per_100g": 400.0}
        )
        assert levels.fat.value == "15.00g/100g"
        assert levels.fat.level == "high"            # 20% DV
        assert levels.saturated_fat.level == "moderate"  # 15% DV
        assert levels.sugars.level == "low"           # 4% DV
        assert levels.sodium.level == "high"          # ~17.4% DV

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0.0, "0.00g/100g"),
            (1.5, "1.50g/100g"),
            (15.0, "15.00g/100g"),
            (119.999, "120.00g/100g"),
        ],
    )
    def test_value_formatting_two_decimals(self, value, expected):
        levels = NutrientService().compute_nutrient_levels({"fat_per_100g": value})
        assert levels.fat.value == expected


class TestDailyValueBoundaries:
    """Boundary values that land exactly on the 5% and 15% thresholds."""

    def test_exactly_five_percent_is_low(self):
        # fat DV = 75g -> 5% = 3.75g
        levels = NutrientService().compute_nutrient_levels({"fat_per_100g": 3.75})
        assert levels.fat.level == "low"

    def test_just_above_five_percent_is_moderate(self):
        levels = NutrientService().compute_nutrient_levels({"fat_per_100g": 3.76})
        assert levels.fat.level == "moderate"

    def test_exactly_fifteen_percent_is_moderate(self):
        # fat DV = 75g -> 15% = 11.25g
        levels = NutrientService().compute_nutrient_levels({"fat_per_100g": 11.25})
        assert levels.fat.level == "moderate"

    def test_just_above_fifteen_percent_is_high(self):
        levels = NutrientService().compute_nutrient_levels({"fat_per_100g": 11.26})
        assert levels.fat.level == "high"


class TestMissingValues:
    def test_none_value_yields_unknown(self):
        levels = NutrientService().compute_nutrient_levels({"fat_per_100g": None})
        assert levels.fat.value is None
        assert levels.fat.level == "unknown"

    def test_missing_column_yields_unknown(self):
        levels = NutrientService().compute_nutrient_levels({})
        assert levels.fat.value is None
        assert levels.fat.level == "unknown"
        assert levels.sodium.value is None
        assert levels.sodium.level == "unknown"


class TestServingBasedLevels:
    """%DV computed on the parsed serving size instead of 100 g."""

    def test_scales_to_serving(self):
        # 15 g/100g fat, 30 g serving -> 4.5 g -> 6% DV -> moderate
        levels = NutrientService().compute_nutrient_levels(
            {"fat_per_100g": 15.0, "serving_size": "30 g"}
        )
        assert levels.fat.value == "4.50g/serving"
        assert levels.fat.level == "moderate"

    def test_sodium_mg_scaling(self):
        # 400 mg/100g sodium, 30 g serving -> 120 mg -> ~5.2% DV -> moderate
        levels = NutrientService().compute_nutrient_levels(
            {"sodium_per_100g": 400.0, "serving_size": "30 g"}
        )
        assert levels.sodium.value == "120.00mg/serving"
        assert levels.sodium.level == "moderate"

    @pytest.mark.parametrize(
        ("serving_size", "expected_value"),
        [
            ("250 ml", "37.50g/serving"),   # ml treated as grams (density ~1)
            ("1 kg", "150.00g/serving"),
            ("0.5 l", "75.00g/serving"),
            ("30g", "4.50g/serving"),       # no space
        ],
    )
    def test_unit_parsing(self, serving_size, expected_value):
        levels = NutrientService().compute_nutrient_levels(
            {"fat_per_100g": 15.0, "serving_size": serving_size}
        )
        assert levels.fat.value == expected_value

    def test_unparseable_serving_falls_back_to_100g(self):
        levels = NutrientService().compute_nutrient_levels(
            {"fat_per_100g": 15.0, "serving_size": "2 cookies"}
        )
        assert levels.fat.value == "15.00g/100g"
        assert levels.fat.level == "high"

    def test_missing_serving_falls_back_to_100g(self):
        levels = NutrientService().compute_nutrient_levels({"fat_per_100g": 15.0})
        assert levels.fat.value == "15.00g/100g"

    def test_boundary_on_serving_basis(self):
        # fat DV = 75 g; 5% of DV = 3.75 g per serving -> 25 g serving needs 15 g/100g
        levels = NutrientService().compute_nutrient_levels(
            {"fat_per_100g": 15.0, "serving_size": "25 g"}
        )
        assert levels.fat.level == "low"