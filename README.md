# e-store-extension-canada-api

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](.python-version)

Backend REST API for the Canadian e-store browser extension
([offCanada](https://github.com/offCanada)). Given a product id or UPC barcode, it
returns product metadata plus computed nutrition indicators: a Nutri-Score letter
grade (a–e) and low/moderate/high levels for fat, saturated fat, sugars, and sodium
based on Health Canada daily values.

## Quickstart

Requires Python 3.14+ and [uv](https://astral.sh/uv).

```bash
git clone https://github.com/offCanada/e-store-extension-canada-api.git
cd e-store-extension-canada-api
uv sync          # install deps into .venv
uv run serve     # dev server on http://127.0.0.1:8000 (auto-reload)
uv run pytest    # test suite + coverage
```

A pre-built database ships at `app/data/nutrilens.duckdb` — no data setup needed.

## Configuration

Optional `.env` in the project root — see [.env.example](.env.example) for a
commented template.

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `<repo>/app/data/nutrilens.duckdb` | Path to the DuckDB file |
| `READ_ONLY` | `true` | Open read-only (file must exist) |
| `ALLOWED_ORIGINS` | `["*"]` | CORS origins — restrict in production |

## API

Single versioned endpoint, rate limited to **30 req/min per IP**:

```
GET /api/v1/products/search?product_id=<id>&code=<upc>
```

At least one of `product_id` or `code` is required (both = AND match).
Interactive docs: [/docs](http://localhost:8000/docs) and `/redoc` once running.

```bash
curl "http://localhost:8000/api/v1/products/search?code=055742561111"
```

```json
{
  "status": true,
  "message": "product found",
  "product": {
    "barcode": "055742561111", "product_id": "584600EA",
    "brand": "Compliments", "title": "Sliced Almonds",
    "image_url": "https://voila.ca/images-v3/2d92d19c-0354-49c0-8a91-5260ed0bf531/97b03e44-9b24-49ad-a2a0-460e752712c4/300x300.jpg",
    "taxonomy": "Snacks", "size": "275g", "serving_size": "30 g",
    "scores": { "nutri_score": "unknown", "eco_score": "a", "nova_score": "3" },
    "nutrient_levels": {
      "fat":           { "value": "16.00g/serving", "level": "high" },
      "saturated_fat": { "value": "1.50g/serving",  "level": "moderate" },
      "sugars":        { "value": "1.00g/serving",  "level": "low" },
      "sodium":        { "value": "2.00mg/serving", "level": "low" }
    },
    "match_type": "direct"
  },
  "error": null
}
```

Errors share the same envelope with `"status": false`. The OpenAPI schema
(`/openapi.json`) is the canonical full contract.

> `eco_score` and `nova_score` are **random placeholders** until real values are populated in database

## Nutrient Levels

Each nutrient level comes from a %DV computed on the **serving size**: the
per-100g amount is scaled by the parsed `serving_size` (units `g`, `kg`, `mg`,
`l`, `ml` — ml ≈ g), then classified against Health Canada daily values:

- **low** ≤ 5% DV · **moderate** ≤ 15% DV · **high** > 15% DV

Example: 15 g fat per 100 g with a 30 g serving → 4.5 g per serving → 6% of the
75 g daily value → `moderate`. Missing serving sizes fall back to a per-100g
basis (`…/100g` in the value); missing nutrients are `unknown`.
Reference values: fat 75 g, saturated fat 20 g, sugars 100 g, sodium 2,300 mg.

## Data & Known Gaps

The dataset is committed (`app/data/nutrilens.duckdb`, built from the Parquet
sources in `app/data/dataset/`). To rebuild after swapping Parquet files:

```bash
mkdir -p database && ln -s ../app/data/dataset database/dataset  # ETL hardcodes ./database/
uv run python app/data/extract_dataset.py
mv database/nutrilens.duckdb app/data/nutrilens.duckdb
```

Known gaps — each is a good first issue:

- `eco_score` / `nova_score` return random placeholders (above)
- Search params (`name`, `brand`, `category`, `quantity`, `search_query`) are
  accepted but ignored — only direct lookup by `product_id`/`code` works
- ETL script uses hardcoded `./database/` paths (workaround above)
- Rate limiter is in-memory: resets on restart, not shared across workers/processes

## Project Structure

```
app/
├── main.py               # FastAPI assembly (lifespan, CORS, routes)
├── configs/              # settings (.env), DuckDB connection, rate limiter
├── models/               # Pydantic request/response models + validation
├── routers/products.py   # GET /api/v1/products/search handler
├── services/             # lookup orchestration, Nutri-Score mapping, %DV levels
├── exceptions/           # domain errors + unified JSON error envelope
└── data/                 # Parquet sources, ETL script, nutrilens.duckdb
tests/                    # pytest suite mirroring app/ layout
```

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Questions?
[Open an issue](https://github.com/offCanada/e-store-extension-canada-api/issues).

By participating you agree to the [AGPL-3.0](LICENSE) license terms. 

## Troubleshooting

- **Port in use:** `uv run python -m uvicorn app.main:app --port 8001`
- **Python version:** must be 3.14+ (`python --version`)
- **Startup DB errors:** with `READ_ONLY=true` the file at `DB_PATH` must exist;
  relative paths resolve from your working directory — prefer absolute paths
