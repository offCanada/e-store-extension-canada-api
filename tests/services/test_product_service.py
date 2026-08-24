import pytest

from app.models.product import MatchType
from app.models.product_search_params import ProductSearchParams
from app.services.product_service import ProductService


class TestComputeNutriScore:
    @pytest.mark.parametrize(
        ("points", "expected"),
        [
            (-5, "a"),
            (0, "a"),
            (1, "b"),
            (2, "b"),
            (3, "c"),
            (10, "c"),
            (11, "d"),
            (18, "d"),
            (19, "e"),
            (42, "e"),
        ],
    )
    def test_thresholds(self, points, expected):
        assert ProductService(con=None).compute_nutri_score(points) == expected

    @pytest.mark.parametrize("points", [None, "abc", "5"])
    def test_non_numeric_yields_unknown(self, points):
        assert ProductService(con=None).compute_nutri_score(points) == "unknown"


class TestLookupByIds:
    def test_by_code(self, db, product_service):
        product = product_service.lookup_by_ids(None, "055742561111")
        assert product is not None
        assert product["upc"] == "055742561111"

    def test_by_product_id(self, db, product_service):
        product = product_service.lookup_by_ids("584600EA", None)
        assert product is not None
        assert product["external_id"] == "584600EA"

    def test_by_both(self, db, product_service):
        product = product_service.lookup_by_ids("584600EA", "055742561111")
        assert product is not None

    def test_no_match_returns_none(self, db, product_service):
        assert product_service.lookup_by_ids(None, "999999999999") is None

    def test_no_identifiers_returns_none(self, db, product_service):
        assert product_service.lookup_by_ids(None, None) is None


class TestFind:
    def test_found_returns_direct_product(self, db, product_service):
        product = product_service.find(ProductSearchParams(code="055742561111"))
        assert product is not None
        assert product.barcode == "055742561111"
        assert product.match_type == MatchType.DIRECT

    def test_not_found_returns_none(self, db, product_service):
        assert product_service.find(ProductSearchParams(code="999999999999")) is None


class TestBuildProduct:
    def test_field_mapping(self, product_service):
        product = product_service.build_product(
            {
                "upc": "055742561111",
                "external_id": "584600EA",
                "brand": "Compliments",
                "core_title": "Sliced Almonds",
                "image_url": "http://img/a.jpg",
                "reference_db_taxonomy": "MEAT_SEAFOOD",
                "size": "275g",
                "serving_size": "30 g",
                "nutri_score_points": 5.0,
                "fat_per_100g": 15.0,
                "saturated_fat_per_100g": 3.0,
                "sugars_per_100g": 4.0,
                "sodium_per_100g": 400.0,
            },
            MatchType.DIRECT,
        )
        assert product.barcode == "055742561111"
        assert product.product_id == "584600EA"
        assert product.taxonomy == "Meat_Seafood"
        assert product.match_type == MatchType.DIRECT
        assert product.scores.nutri_score == "c"
        assert product.nutrient_levels.fat.level == "moderate"  # 4.5 g on a 30 g serving = 6% DV


class TestComputeScores:
    def test_nutri_score_derived_from_points(self, product_service):
        scores = product_service.compute_scores({"nutri_score_points": 5.0})
        assert scores.nutri_score == "c"

    def test_eco_and_nova_within_placeholder_ranges(self, product_service):
        scores = product_service.compute_scores({"nutri_score_points": 5.0})
        assert scores.eco_score in ["a", "b", "c", "d", "e"]
        assert scores.nova_score in ["1", "2", "3", "4"]