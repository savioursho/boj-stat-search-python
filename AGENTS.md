# Repository Guidelines

## Project Structure & Module Organization

- Main package: `src/boj_stat_search/`.
- `core/`: pure functions and shared logic (`url_builder.py`, `validator.py`, `parser.py`, `types.py`, `database.py`).
- `api/`: side-effect functions that call HTTP endpoints (`api_request.py`).
- `models/`: dataclasses and typed response objects.
- Tests: `tests/` (`test_api_request.py`, `test_parser.py`, `test_url_builder.py`, `test_validator.py`).
- Reference docs and experiments: `notes/` and `docs/` (not production code).

## Build, Test, and Development Commands

- Install/sync environment: `uv sync`
- Run tests: `uv run pytest -q`
- Run a specific test file: `uv run pytest -q tests/test_validator.py`
- Lint: `uv run ruff check src tests`
- Format: `uv run ruff format`
- Type check: `uv run ty check`
- Run both checks before PR:
  - `uv run ruff format`
  - `uv run ruff check src tests`
  - `uv run ty check`
  - `uv run pytest -q`

## Coding Style & Naming Conventions

- Python 3.12+, 4-space indentation, UTF-8 text.
- Keep modules aligned to architecture:
  - pure logic in `core/`,
  - I/O in `api/`,
  - dataclasses/types in `models/`.
- Naming:
  - functions/variables/modules: `snake_case`
  - dataclasses/classes: `PascalCase`
  - constants: `UPPER_SNAKE_CASE`
- Favor explicit typing (existing code uses `Literal`, `dict[str, Any]`, dataclasses).
- Use `ruff` as the style gate; do not merge with lint failures.

## Testing Guidelines

- Framework: `pytest`.
- Test files: `tests/test_*.py`; test functions: `test_*`.
- Add or update tests for every behavior change, especially:
  - URL building,
  - validation modes (`raise`, `warn`, `ignore`),
  - API request pass-through behavior using mock clients.
- Avoid real network calls in unit tests; use `unittest.mock.Mock`.

## Commit & Pull Request Guidelines

- Current history uses generic messages like `update`; prefer descriptive, imperative commits (for example, `add metadata validation warnings`).
- Keep commits focused and logically grouped.
- PRs should include:
  - what changed and why,
  - affected modules/APIs,
  - test evidence (`uv run pytest -q` output),
  - any compatibility notes (signature or validation behavior changes).
