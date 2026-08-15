import pytest
from pydantic import ValidationError

from app.models.product_search_params import ProductSearchParams


class TestCodeValidation:
    def test_valid_code_accepted(self):
        params = ProductSearchParams(code="055742561111")
        assert params.code == "055742561111"

    def test_six_digit_code_accepted(self):
        params = ProductSearchParams(code="123456")
        assert params.code == "123456"

    def test_non_digit_code_rejected(self):
        with pytest.raises(ValidationError):
            ProductSearchParams(code="05574256111a")

    def test_too_short_code_rejected(self):
        with pytest.raises(ValidationError):
            ProductSearchParams(code="12345")

    def test_too_long_code_rejected(self):
        with pytest.raises(ValidationError):
            ProductSearchParams(code="055742561111743")


class TestSearchQueryValidation:
    def test_query_is_trimmed(self):
        params = ProductSearchParams(code="055742561111", search_query="  almonds  ")
        assert params.search_query == "almonds"

    def test_blank_query_becomes_none(self):
        with pytest.raises(ValidationError):
            ProductSearchParams(search_query="   ")

    def test_too_long_query_rejected(self):
        with pytest.raises(ValidationError):
            ProductSearchParams(search_query="a" * 251)


class TestAtLeastOneRequired:
    def test_no_identifier_rejected(self):
        with pytest.raises(ValidationError):
            ProductSearchParams(name="anything")

    def test_product_id_satisfies_requirement(self):
        params = ProductSearchParams(product_id="584600EA")
        assert params.product_id == "584600EA"

    def test_code_satisfies_requirement(self):
        params = ProductSearchParams(code="055742561111")
        assert params.code == "055742561111"

    def test_both_identifiers_allowed(self):
        params = ProductSearchParams(product_id="584600EA", code="055742561111")
        assert params.product_id == "584600EA"
        assert params.code == "055742561111"

    def test_empty_code_with_other_fields_rejected(self):
        with pytest.raises(ValidationError):
            ProductSearchParams(code="", name="shfsd")

    def test_empty_code_with_product_id_allowed(self):
        params = ProductSearchParams(code="", product_id="584600EA")
        assert params.product_id == "584600EA"
        assert params.code is None

    def test_empty_optional_fields_allowed(self):
        params = ProductSearchParams(code="055742561111", brand="", category="  ")
        assert params.code == "055742561111"
        assert params.brand is None
        assert params.category is None