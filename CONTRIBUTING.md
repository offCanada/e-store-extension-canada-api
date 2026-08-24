# Contributing

Thanks for helping! Setup takes two minutes.

## Setup

Requires Python 3.14+ and [uv](https://astral.sh/uv).

```bash
git clone https://github.com/offCanada/e-store-extension-canada-api.git
cd e-store-extension-canada-api
uv sync        # installs deps + creates .venv
uv run pytest  # should pass (~64 tests, ~95% coverage)
```

Optional: `cp .env.example .env` to tweak settings.

## Tests

- `uv run pytest` — coverage of `app/` runs automatically
- The suite is hermetic: in-memory DuckDB fixtures, no network, never touches
  `app/data/nutrilens.duckdb`
- New endpoints need success, validation-error, and not-found cases; add
  service/model tests next to the code they cover

## Branches & Commits

Branch off `main` using `feat/`, `fix/`, `test/`, or `docs/` prefixes.

Commits follow [Conventional Commits](https://www.conventionalcommits.org/) —
lowercase imperative summary:

| Type | Use for |
|---|---|
| `feat` | New functionality |
| `fix` | Bug fixes |
| `test` | Test-only changes |
| `docs` | Documentation |
| `chore` | Tooling/config |

## Pull Requests

1. Title follows Conventional Commits (e.g., `feat: add text search fallback`)
2. `uv run pytest` passes locally
3. Update the README if behavior or configuration changed

Squash-and-merge is used; a maintainer will review shortly.

## Where to Help

See the known-gaps list in the [README](README.md#data--known-gaps) — several are
good-first-issue sized — or browse open issues.

## License

By contributing you agree your contributions are licensed under the
[AGPL-3.0 License](LICENSE).
