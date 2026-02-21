# boj-stat-search

Python client for the Bank of Japan Stat-Search API.

## Quick Start

```python
from boj_stat_search import get_metadata

metadata = get_metadata(db="FM01")
print(metadata.status, metadata.db, len(metadata.result_set))
```

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
