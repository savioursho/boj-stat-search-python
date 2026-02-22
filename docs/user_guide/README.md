# User Guide

This guide explains how to use `boj_stat_search` for common tasks.

The package can be used in three ways:

- **CLI** — the `boj-stat-search` command lets you query data directly from the terminal. JSON output is designed for piping to `jq` and other tools.
- **Functional API** — top-level functions (`get_metadata`, `get_data_code`, `get_data_layer`, `generate_metadata_parquet_files`, `load_catalog_db`, `load_catalog_all`). Simple and composable; no built-in throttling, so callers must manage delays manually for batch use.
- **`BojClient`** — a stateful client that wraps the functional API. Reuses a single HTTP connection and enforces a configurable minimum delay between requests (default 1 s). Preferred for batch workflows.

## Who This Is For

- Users who want to fetch metadata or time-series data from BOJ Stat-Search.
- Users who prefer typed helpers like `Frequency`, `Layer`, and `Period`.
- Users who want to inspect layer trees quickly with `show_layers`.

## Guide Map

1. [Getting Started](./getting_started.md)
2. [Querying Data](./querying_data.md)
3. [Layer Tree Display](./layer_tree_display.md)
4. [Command-Line Interface](./cli.md)

## Coverage

- Covered:
  - `get_metadata`
  - `get_data_code`
  - `get_data_layer`
  - `generate_metadata_parquet_files`
  - `load_catalog_db`
  - `load_catalog_all`
  - `BojClient` (stateful client with built-in throttling)
  - `show_layers`
  - `list_db`
  - `Frequency`, `Layer`, `Period`
  - `BojApiError`
  - `DataResponse`, `MetadataResponse`, `DbInfo`
  - Pagination, error handling, HTTP client reuse, throttling
- Not covered:
  - raw API variants (`get_*_raw`)
  - low-level URL builders, validators, and parsers
