from app.configs.limiter import limiter


class TestGetProductSearch:
    def test_found_product_returns_200_envelope(self, client):
        response = client.get("/api/v1/products/search", params={"code": "055742561111"})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] is True
        assert body["message"] == "product found"
        assert body["error"] is None
        assert body["product"]["barcode"] == "055742561111"
        assert body["product"]["nutrient_levels"]["fat"]["level"] == "high"

    def test_product_with_null_nutrients_returns_unknown(self, client):
        response = client.get("/api/v1/products/search", params={"code": "000000000002"})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] is True
        assert body["product"]["scores"]["nutri_score"] == "unknown"
        assert body["product"]["nutrient_levels"]["fat"]["level"] == "unknown"
        assert body["product"]["nutrient_levels"]["fat"]["value"] is None

    def test_not_found_returns_404_envelope(self, client):
        response = client.get("/api/v1/products/search", params={"code": "999999999999"})
        assert response.status_code == 404
        body = response.json()
        assert body["status"] is False
        assert body["message"] == "product not found"
        assert body["product"] is None
        assert body["error"] == "product not found"

    def test_invalid_code_returns_422_without_product(self, client):
        response = client.get("/api/v1/products/search", params={"code": "055742561111743"})
        assert response.status_code == 422
        body = response.json()
        assert body["status"] is False
        assert body["message"] == "invalid request parameters"
        assert "error" in body
        assert "product" not in body

    def test_no_params_returns_422(self, client):
        response = client.get("/api/v1/products/search")
        assert response.status_code == 422
        body = response.json()
        assert body["status"] is False
        assert "product" not in body

    def test_search_by_product_id(self, client):
        response = client.get("/api/v1/products/search", params={"product_id": "584600EA"})
        assert response.status_code == 200
        assert response.json()["product"]["product_id"] == "584600EA"

    def test_null_serving_size_returns_200_with_none(self, client):
        response = client.get("/api/v1/products/search", params={"code": "000000000003"})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] is True
        assert body["product"]["serving_size"] is None
        assert body["product"]["brand"] == "Brand Y"
        assert body["product"]["taxonomy"] == "Juice"
        assert body["product"]["scores"]["nutri_score"] == "b"


class TestRateLimit:
    def test_rate_limit_returns_429_envelope(self, client):
        limiter.enabled = True
        try:
            limiter._storage.reset()
            for _ in range(30):
                client.get("/api/v1/products/search", params={"code": "999999999999"})
            response = client.get("/api/v1/products/search", params={"code": "999999999999"})
            assert response.status_code == 429
            body = response.json()
            assert body["status"] is False
            assert body["message"] == "rate limit exceeded"
            assert "error" in body
            assert "product" not in body
        finally:
            limiter.enabled = False