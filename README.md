# boj-stat-search

**Unofficial** Python client for the [Bank of Japan Time Series Statistical Data Search Site (日本銀行時系列統計データ検索サイト)](https://www.stat-search.boj.or.jp/) API. This package is not affiliated with or endorsed by the Bank of Japan.

## Installation

```bash
pip install git+https://github.com/savioursho/boj-stat-search-python.git
```

or with uv:

```bash
uv add git+https://github.com/savioursho/boj-stat-search-python.git
```

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

```python
from boj_stat_search import get_metadata, show_layers

metadata = get_metadata(db="BP01")
show_layers(metadata.result_set, layer="1,1")
```

```bash
# Generate per-DB metadata Parquet files locally
boj-stat-search generate-metadata-parquet --output-dir metadata
```

```python
from boj_stat_search import load_catalog_db

# Download/cache metadata/FM01.parquet locally (24h TTL by default)
fm01_catalog = load_catalog_db("FM01")
print(fm01_catalog.num_rows)
```

```python
from boj_stat_search import search_series

# Search across local catalog metadata (cached automatically)
results = search_series("exchange rate", db="FM01")
print(results[0].series_code if results else "no match")
```

```python
from boj_stat_search import list_series

# List all series in one DB from the local catalog
series = list_series("FM08")
print(len(series))
```

## Documentation

- [Documentation Home](./docs/README.md)
- [User Guide](./docs/user_guide/README.md)
- [Development Guide](./docs/development_guide/README.md)
- [Metadata Licensing Determination](./docs/development_guide/metadata_licensing.md)

## Official Resources

- [API 公開についてのお知らせ (API Release Notice)](https://www.boj.or.jp/statistics/outline/notice_2026/not260218a.htm)
- [API マニュアル (API Manual)](https://www.stat-search.boj.or.jp/info/api_manual.pdf)
- [API 利用上の注意事項 (API Terms of Use)](https://www.stat-search.boj.or.jp/info/api_notice.pdf)

## Credit

このサービスは、日本銀行時系列統計データ検索サイトの API 機能を使用しています。サービスの内容は日本銀行によって保証されたものではありません。

This service uses the API of the [Bank of Japan Time Series Statistical Data Search Site](https://www.stat-search.boj.or.jp/). The contents of this service are not guaranteed by the Bank of Japan.
