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

## Parameter Helpers

- `Frequency`: enum for valid frequency values (`CY`, `FY`, `CH`, `FH`, `Q`, `M`, `W`, `D`)
- `Layer`: helper for layer paths (`Layer(1, 1, 1)`, `Layer("*")`)
- `Period`: helper for date values
  - `Period.year(2025)`
  - `Period.half(2025, 1)`
  - `Period.quarter(2025, 2)`
  - `Period.month(2025, 9)`

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
    Frequency,
    Layer,
    Period,
    get_data_code,
    get_data_layer,
)
```

## Next Step

Continue to [Layer Tree Display](./layer_tree_display.md).
