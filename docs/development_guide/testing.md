# Testing Strategy

Part of the [Development Guide](./README.md). See
[Architecture](./architecture.md) for the module boundary this strategy follows.

This project uses a Functional Core / Imperative Shell architecture (see
`docs/development_guide/architecture.md`). Our tests follow the same boundary:

- `core/` tests are comprehensive and logic-focused.
- `shell/` tests are thin and boundary-focused.

## Testing Principles

1. Mirror architecture boundaries in tests.
2. Put business and transformation logic tests in `core` targets.
3. Keep `shell` tests lightweight: verify orchestration, side effects, and
   integration boundaries only.
4. Avoid real network calls in unit tests.
5. Use descriptive test names that describe behavior, not implementation.

## `tests/` Directory Structure

`tests/` should mirror the same Functional Core / Imperative Shell boundary as
`src/boj_stat_search/`.

Target structure:

```text
tests/
├── core/
│   ├── test_types.py
│   ├── test_validator.py
│   ├── test_url_builder.py
│   ├── test_parser.py
│   ├── test_formatter.py
│   └── test_catalog_parser.py
└── shell/
    ├── test_api_request.py
    ├── test_client.py
    ├── test_cli.py
    ├── test_display.py
    ├── test_catalog_loader.py
    ├── test_catalog_search.py
    ├── test_metadata_export.py
    └── test_public_api.py
```

### Core-Oriented Test Modules

These target modules under `src/boj_stat_search/core/` and should remain
logic-heavy.

| Test file | Primary target |
|---|---|
| `tests/core/test_types.py` | `core/types.py` |
| `tests/core/test_validator.py` | `core/validator.py` |
| `tests/core/test_url_builder.py` | `core/url_builder.py` |
| `tests/core/test_parser.py` | `core/parser.py` |
| `tests/core/test_formatter.py` | `core/formatter.py` |
| `tests/core/test_catalog_parser.py` | `core/catalog_parser.py` |

### Shell-Oriented Test Modules

These target modules under `src/boj_stat_search/shell/` and should remain
thin.

| Test file | Primary target |
|---|---|
| `tests/shell/test_api_request.py` | `shell/api.py` |
| `tests/shell/test_client.py` | `shell/client.py` |
| `tests/shell/test_cli.py` | `shell/cli.py` |
| `tests/shell/test_display.py` | `shell/display.py` |
| `tests/shell/test_catalog_loader.py` | `shell/catalog/loader.py` |
| `tests/shell/test_catalog_search.py` | `shell/catalog/search.py` |
| `tests/shell/test_metadata_export.py` | `shell/catalog/exporter.py` |

### Public API Surface

| Test file | Primary target |
|---|---|
| `tests/shell/test_public_api.py` | top-level re-export contract in `src/boj_stat_search/__init__.py` |

## Core Testing Strategy (Comprehensive / Heavy)

For `core` targets:

- Do not use test doubles (no `Mock`, `patch`, `monkeypatch`) to simulate core
  behavior.
- Test real logic with representative and edge-case inputs.
- Prefer broad scenario matrices, including:
  - valid/happy-path transformations,
  - invalid/edge inputs,
  - explicit error messages and modes (`raise`, `warn`, `ignore`) where
    applicable,
  - boundary values for parsing, validation, and formatting.
- Assert final values and structures, not intermediate implementation details.

Rationale: `core` is where correctness lives. Tests should maximize confidence
in deterministic behavior.

## Shell Testing Strategy (Thin / Lightweight)

For `shell` targets:

- Use test doubles as needed for external boundaries:
  - HTTP clients/responses,
  - filesystem and cache boundaries,
  - CLI output and process-facing behavior.
- Verify orchestration and contracts:
  - correct call delegation,
  - correct argument forwarding to `core`,
  - error propagation/translation,
  - expected side effects at the boundary.
- Do not duplicate `core` logic tests in `shell` tests.

Rationale: `shell` should coordinate side effects, not own business logic.

## Rule of Thumb for New Tests

1. If behavior is pure and deterministic, place it in `core` and test it
   heavily without doubles. Put the test module under `tests/core/`.
2. If behavior touches I/O, HTTP, CLI, or mutable runtime state, keep it in
   `shell` and test it with thin boundary tests (using doubles when needed).
   Put the test module under `tests/shell/`.
3. If a `shell` module accumulates non-trivial logic, move that logic into
   `core` and add comprehensive `core` tests there.

## Test Commands

```bash
uv run pytest -q
uv run ruff check src tests
uv run ty check
```
