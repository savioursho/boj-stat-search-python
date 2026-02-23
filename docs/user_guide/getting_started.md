# Getting Started

Run one request successfully using only top-level imports.

## 1. Install

```bash
pip install git+https://github.com/savioursho/boj-stat-search-python.git
```

or with uv:

```bash
uv add git+https://github.com/savioursho/boj-stat-search-python.git
```

For local development, clone the repository and run:

```bash
uv sync
```

## 2. Inspect Available DB Names

```python
from boj_stat_search import list_db

db_list = list_db()
print(db_list[0].name, db_list[0].desc)
```

Use one of these DB names (for example, `FM01`, `BP01`, `MD10`) in API calls.

## 3. First Metadata Request

```python
from boj_stat_search import get_metadata

metadata = get_metadata(db="FM01")
print(metadata.status)
print(metadata.db)
print(len(metadata.result_set))
```

`get_metadata` returns a `MetadataResponse` object. Common first checks are:

- `status`: API status code in response body
- `db`: database name returned by the API
- `result_set`: metadata entries

## 4. Data Code Input Styles

`get_data_code` supports multiple input styles:

```python
from boj_stat_search import Code, get_data_code

# Explicit db + plain series code
response_a = get_data_code(db="IR01", code="MADR1Z@D")

# BOJ UI-style DB'CODE format
response_b = get_data_code(code=Code("IR01'MADR1Z@D"))

# Omit db (best-effort cache-based resolution)
response_c = get_data_code(code="MADR1Z@D")
```

DB auto-resolution uses local cached catalog files only. It does not download metadata.
If DB cannot be resolved from cache, provide `db` explicitly (or preload cache via `load_catalog_all` / `load_catalog_db`).

## Two API Styles

`boj_stat_search` provides two ways to make requests:

|                       | Functional API                          | `BojClient`                                  |
|-----------------------|-----------------------------------------|----------------------------------------------|
| Import                | `from boj_stat_search import get_metadata` | `from boj_stat_search import BojClient`   |
| HTTP connection reuse | Manual (`client=` kwarg)                | Automatic                                    |
| Throttling            | Manual (`time.sleep`)                   | Automatic (default 1 s between requests)     |
| Best for              | One-off calls                           | Batch workflows                              |

The rest of this guide covers the functional API. For the stateful client, see [Querying Data — BojClient](./querying_data.md#bojclient--throttling-and-connection-reuse).

## Top-Level API Used Here

```python
from boj_stat_search import Code, get_data_code, get_metadata, list_db
```

## Next Step

Continue to [Querying Data](./querying_data.md).
