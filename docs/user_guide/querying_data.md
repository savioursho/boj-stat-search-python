# Querying Data

Fetch time-series values with typed parameters from the top-level API.

## Data by Series Code

Use `get_data_code` when you already know series codes.

```python
from boj_stat_search import Period, get_data_code

response = get_data_code(
    db="CO",
    code="TK99F1000601GCQ01000,TK99F2000601GCQ01000",
    start_date=Period.quarter(2024, 1),
    end_date=Period.quarter(2025, 4),
)

print(response.status, len(response.result_set))
```

## Series Discovery with Local Catalog

Use `search_series` to find candidate series codes from locally cached metadata.

```python
from boj_stat_search import Layer, search_series

results = search_series("exchange rate", db="FM01", layer=Layer(1, "*"))
for entry in results[:5]:
    print(entry.db, entry.series_code, entry.name_en)
```

Use `list_series` to list every series in one DB.

```python
from boj_stat_search import list_series

series = list_series("FM08")
for entry in series[:5]:
    print(entry.series_code, entry.name_en)
```

## Data by Layer + Frequency

Use `get_data_layer` to query by hierarchy.

```python
from boj_stat_search import Frequency, Layer, Period, get_data_layer

response = get_data_layer(
    db="BP01",
    frequency=Frequency.MONTHLY,
    layer=Layer(1, 1, 1),
    start_date=Period.month(2025, 4),
    end_date=Period.month(2025, 9),
)

print(response.status, len(response.result_set))
```

## Reading DataResponse Results

`DataResponse.result_set` is a `tuple[dict[str, Any], ...]`. Each entry is a dict with these typical keys:

- `SERIES_CODE` — the series identifier
- `VALUES` — a dict containing:
  - `SURVEY_DATES` — list of date strings for each observation
  - `VALUES` — list of value strings for each observation

```python
for entry in response.result_set:
    print(entry["SERIES_CODE"])
    for date, value in zip(
        entry["VALUES"]["SURVEY_DATES"],
        entry["VALUES"]["VALUES"],
    ):
        print(f"  {date}: {value}")
```

## Pagination

The BOJ API paginates large result sets. `DataResponse` exposes `next_position: int | None` — when it is not `None`, more pages are available.

Pass `start_position` to fetch the next page:

```python
from boj_stat_search import Frequency, Layer, Period, get_data_layer

results = []
start_position = None

while True:
    response = get_data_layer(
        db="BP01",
        frequency=Frequency.MONTHLY,
        layer=Layer(1, 1, 1),
        start_date=Period.month(2025, 4),
        end_date=Period.month(2025, 9),
        start_position=start_position,
    )
    results.extend(response.result_set)

    if response.next_position is None:
        break
    start_position = response.next_position

print(f"Total entries: {len(results)}")
```

`get_data_code` supports the same `start_position` parameter.

## Error Handling

When the BOJ API returns an HTTP error (4xx/5xx), a `BojApiError` is raised. It extends `httpx.HTTPStatusError` and carries extra fields from the BOJ response body:

- `boj_status` (`int | None`) — the `STATUS` field from the BOJ JSON response
- `message_id` (`str | None`) — the `MESSAGEID` field
- `boj_message` (`str | None`) — the `MESSAGE` field

```python
from boj_stat_search import BojApiError, get_metadata

try:
    response = get_metadata(db="INVALID")
except BojApiError as exc:
    print(exc.boj_status)    # e.g. 404
    print(exc.message_id)    # e.g. "ERR_001"
    print(exc.boj_message)   # human-readable error from BOJ
    print(exc.response)      # the underlying httpx.Response
```

## Reusing an HTTP Client

All API functions accept an optional `client` keyword argument (`httpx.Client | None`). Passing a shared client reuses the underlying TCP connection, which is useful for batched calls or pagination loops:

```python
import httpx
from boj_stat_search import get_metadata, list_db

with httpx.Client() as client:
    for db_info in list_db():
        response = get_metadata(db_info.name, client=client)
        print(db_info.name, len(response.result_set))
```

**Throttling note:** the functional API does not add any delay between requests. For batch loops, add `time.sleep()` manually to avoid overloading the server:

```python
import time

import httpx
from boj_stat_search import get_metadata, list_db

with httpx.Client() as client:
    for db_info in list_db():
        response = get_metadata(db_info.name, client=client)
        print(db_info.name, len(response.result_set))
        time.sleep(1.0)
```

If you prefer not to manage throttling yourself, use [`BojClient`](#bojclient--throttling-and-connection-reuse) instead.

## BojClient — Throttling and Connection Reuse

`BojClient` is a stateful wrapper that handles both HTTP connection reuse and request throttling automatically. Use it as a drop-in replacement for the functional API in batch workflows.

```python
from boj_stat_search import BojClient, list_db

with BojClient() as client:
    for db_info in list_db():
        response = client.get_metadata(db_info.name)
        print(db_info.name, len(response.result_set))
```

By default, `BojClient` waits at least **1 second between consecutive requests**. Adjust with `min_request_interval`:

```python
BojClient(min_request_interval=2.0)  # wait at least 2 s between requests
BojClient(min_request_interval=0)    # no throttling (use with care)
```

`BojClient` exposes the same three methods as the functional API — `get_metadata`, `get_data_code`, and `get_data_layer` — with identical signatures. The `on_validation_error` mode is configured once at construction:

```python
from boj_stat_search import BojClient

with BojClient(on_validation_error="warn", min_request_interval=1.0) as client:
    meta = client.get_metadata("BP01")
    data = client.get_data_code("FM01", "STRDCLUCON", start_date="202501")
```

## Parameter Helpers

- `Frequency`: enum for valid frequency values

  | Member             | API value |
  |--------------------|-----------|
  | `CALENDAR_YEAR`    | `CY`      |
  | `FISCAL_YEAR`      | `FY`      |
  | `CALENDAR_HALF`    | `CH`      |
  | `FISCAL_HALF`      | `FH`      |
  | `QUARTERLY`        | `Q`       |
  | `MONTHLY`          | `M`       |
  | `WEEKLY`           | `W`       |
  | `DAILY`            | `D`       |

- `Layer`: helper for layer paths (`Layer(1, 1, 1)`, `Layer("*")`)
- `Period`: helper for date values
  - `Period.year(2025)`
  - `Period.half(2025, 1)`
  - `Period.quarter(2025, 2)`
  - `Period.month(2025, 9)`
  - `Period("202501")` and `Period.from_string("202501")` also work for direct string input.

## Date Notes

- `get_data_code` accepts yearly (`YYYY`) or six-digit (`YYYYMM`) values.
- `get_data_layer` format depends on frequency.
- For weekly/daily layer queries, pass month-format periods (`YYYYMM`) for request parameters.

## Validation Behavior

High-level functions validate parameters before request:

- default: `on_validation_error="raise"`
- alternatives: `"warn"` and `"ignore"`

Example:

```python
from boj_stat_search import get_data_layer

get_data_layer(
    db="MD10",
    frequency="Q",
    layer="*",
    on_validation_error="warn",
)
```

## Top-Level API Used Here

```python
from boj_stat_search import (
    BojApiError,
    BojClient,
    Frequency,
    Layer,
    Period,
    get_data_code,
    get_data_layer,
    list_series,
    search_series,
)
```

## Next Step

Continue to [Layer Tree Display](./layer_tree_display.md).
