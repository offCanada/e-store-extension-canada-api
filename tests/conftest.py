import duckdb
import pytest
from fastapi.testclient import TestClient

from app.configs.db import get_db
from app.configs.limiter import limiter
from app.main import app
from app.services.product_service import ProductService

CREATE_TABLE_SQL = """
CREATE TABLE product_merged (
    external_id VARCHAR,
    upc VARCHAR,
    variant_id VARCHAR,
    reference_db_taxonomy VARCHAR,
    title VARCHAR,
    brand VARCHAR,
    core_title VARCHAR,
    image_url VARCHAR,
    size VARCHAR,
    serving_size VARCHAR,
    normalization_method VARCHAR,
    sugars_per_100g DOUBLE,
    sodium_per_100g DOUBLE,
    fat_per_100g DOUBLE,
    saturated_fat_per_100g DOUBLE,
    nutri_score_points DOUBLE
)
"""

INSERT_SQL = """
INSERT INTO product_merged VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

SEED_ROWS = [
    (
        "584600EA", "055742561111", "v1", "nuts", "Sliced Almonds",
        "Compliments", "Sliced Almonds", "http://img/a.jpg", "275g", "30 g",
        "method", 4.0, 400.0, 15.0, 3.0, 5.0,
    ),
    (
        "AAAAAA", "000000000002", "v2", "water", "Still Water",
        "Brand X", "Still Water", "http://img/b.jpg", "500ml", "250 ml",
        "method", None, None, None, None, None,
    ),
    (
        "BBBBBB", "000000000003", "v3", "juice", "Orange Juice",
        "Brand Y", "Orange Juice", "http://img/c.jpg", "1L", None,
        "method", 6.0, 5.0, 0.1, 0.05, 1.0,
    ),
]


@pytest.fixture
def db():
    con = duckdb.connect(":memory:")
    con.execute(CREATE_TABLE_SQL)
    con.executemany(INSERT_SQL, SEED_ROWS)
    yield con
    con.close()


@pytest.fixture
def product_service(db):
    return ProductService(db)


@pytest.fixture
def client(db):
    limiter.enabled = False

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)