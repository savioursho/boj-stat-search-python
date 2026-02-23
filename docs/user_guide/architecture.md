# Two-Layer API Architecture

`boj_stat_search` is organized into two API layers. Understanding the distinction helps you choose the right functions for your use case.

## Low-Level API

A thin, faithful wrapper around the raw BOJ Stat-Search Web API.

- Parameters are plain strings, matching the upstream API exactly.
- Response structure mirrors the raw JSON response shape.
- No validation, no pagination handling, no multi-request resolution.
- Useful when you need full control or want to replicate raw API behavior.

```python
from boj_stat_search import get_data_code_raw

response = get_data_code_raw(db="IR01", code="MADR1Z@D")
```

## High-Level API

A user-facing layer built on top of the low-level API. This is the layer most users should reach for.

- Accepts value objects (`Frequency`, `Layer`, `Period`) for validation and normalization.
- Automatic pagination — fetches all pages transparently when needed.
- Transparent multi-request resolution — query patterns that require multiple API calls under the hood are handled automatically so you make a single function call.
- Parameter validation with configurable error handling (`raise`, `warn`, `ignore`).

```python
from boj_stat_search import Frequency, Layer, Period, get_data_layer

response = get_data_layer(
    db="BP01",
    frequency=Frequency.MONTHLY,
    layer=Layer(1, 1, 1),
    start_date=Period.month(2025, 4),
    end_date=Period.month(2025, 9),
)
```

## Which Layer Should I Use?

| Concern | Low-level | High-level |
|---|---|---|
| Parameter types | Plain strings | Value objects (`Frequency`, `Layer`, `Period`) |
| Validation | None | Configurable (`raise` / `warn` / `ignore`) |
| Pagination | Manual | Automatic |
| Multi-request resolution | Manual | Automatic |
| Response shape | Mirrors raw API | Parsed into typed objects |
| When to use | Full control, debugging, advanced scripting | Most everyday use cases |

## API Styles per Layer

| Layer | Functional API | `BojClient` | CLI |
|---|---|---|---|
| Low-level | Yes | — | — |
| High-level | Yes | Yes | Yes |

- **Functional API** — stateless functions. Available for both layers.
- **`BojClient`** — adds HTTP connection reuse and automatic throttling. Available for the high-level layer only, where batch workflows are the natural use case.
- **CLI** — each subcommand is a thin wrapper around a high-level function. Low-level API features are not exposed through the CLI; users who need that level of control should use the Python API directly.

## Next Step

The rest of this guide covers the high-level API. For low-level details, refer to the [API Manual](../api_manual/) which documents the upstream endpoints that the low-level layer wraps 1-to-1.
