# User Guide

This guide explains how to use the top-level `boj_stat_search` API for common tasks.

## Who This Is For

- Users who want to fetch metadata or time-series data from BOJ Stat-Search.
- Users who prefer typed helpers like `Frequency`, `Layer`, and `Period`.
- Users who want to inspect layer trees quickly with `show_layers`.

## Guide Map

1. [Getting Started](./getting_started.md)
2. [Querying Data](./querying_data.md)
3. [Layer Tree Display](./layer_tree_display.md)

## Coverage

- Covered:
  - `get_metadata`
  - `get_data_code`
  - `get_data_layer`
  - `show_layers`
  - `list_db`
  - `Frequency`, `Layer`, `Period`
  - `BojApiError`
  - `DataResponse`, `MetadataResponse`, `DbInfo`
  - Pagination, error handling, HTTP client reuse
- Not covered:
  - raw API variants (`get_*_raw`)
  - low-level URL builders, validators, and parsers
