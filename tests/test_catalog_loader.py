from __future__ import annotations

import os
import time
from pathlib import Path
from unittest.mock import Mock

import httpx
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from boj_stat_search.shell.catalog.loader import (
    CatalogCacheError,
    CatalogFetchError,
    load_catalog_all,
    load_catalog_db,
)
from boj_stat_search.core.models import DbInfo


def _parquet_bytes(rows: list[dict[str, str]]) -> bytes:
    table = pa.Table.from_pylist(rows)
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    return sink.getvalue().to_pybytes()


def _write_cached_parquet(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)


def _mock_response(content: bytes) -> Mock:
    response = Mock()
    response.raise_for_status.return_value = None
    response.content = content
    return response


def test_load_catalog_db_downloads_and_caches_on_first_use(tmp_path: Path) -> None:
    client = Mock(spec=httpx.Client)
    client.get.return_value = _mock_response(_parquet_bytes([{"series_code": "A"}]))

    table = load_catalog_db("FM01", cache_dir=tmp_path, client=client)

    assert (tmp_path / "FM01.parquet").exists()
    assert table.column("series_code").to_pylist() == ["A"]
    assert table.column("db").to_pylist() == ["FM01"]
    client.get.assert_called_once_with(
        "https://raw.githubusercontent.com/savioursho/boj-stat-search-python/main/metadata/FM01.parquet"
    )


def test_load_catalog_db_uses_fresh_cache_without_network(tmp_path: Path) -> None:
    cache_path = tmp_path / "FM01.parquet"
    _write_cached_parquet(cache_path, [{"series_code": "CACHED"}])

    client = Mock(spec=httpx.Client)
    table = load_catalog_db(
        "FM01",
        cache_ttl_seconds=3600,
        cache_dir=tmp_path,
        client=client,
    )

    assert table.column("series_code").to_pylist() == ["CACHED"]
    client.get.assert_not_called()


def test_load_catalog_db_refetches_when_cache_is_stale(tmp_path: Path) -> None:
    cache_path = tmp_path / "FM01.parquet"
    _write_cached_parquet(cache_path, [{"series_code": "OLD"}])

    old_time = time.time() - 7200
    os.utime(cache_path, (old_time, old_time))

    client = Mock(spec=httpx.Client)
    client.get.return_value = _mock_response(_parquet_bytes([{"series_code": "NEW"}]))

    table = load_catalog_db(
        "FM01",
        cache_ttl_seconds=60,
        cache_dir=tmp_path,
        client=client,
    )

    assert table.column("series_code").to_pylist() == ["NEW"]
    assert pq.read_table(cache_path).column("series_code").to_pylist() == ["NEW"]
    client.get.assert_called_once()


def test_load_catalog_db_recovers_from_corrupted_fresh_cache(tmp_path: Path) -> None:
    cache_path = tmp_path / "FM01.parquet"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(b"not-parquet")

    client = Mock(spec=httpx.Client)
    client.get.return_value = _mock_response(
        _parquet_bytes([{"series_code": "RECOVERED"}])
    )

    table = load_catalog_db(
        "FM01",
        cache_ttl_seconds=3600,
        cache_dir=tmp_path,
        client=client,
    )

    assert table.column("series_code").to_pylist() == ["RECOVERED"]
    client.get.assert_called_once()


def test_load_catalog_db_raises_fetch_error_on_http_failure(tmp_path: Path) -> None:
    client = Mock(spec=httpx.Client)
    client.get.side_effect = httpx.ConnectError("boom")

    with pytest.raises(CatalogFetchError):
        load_catalog_db("FM01", cache_dir=tmp_path, client=client)


def test_load_catalog_db_raises_cache_error_on_invalid_parquet(tmp_path: Path) -> None:
    client = Mock(spec=httpx.Client)
    client.get.return_value = _mock_response(b"definitely-not-parquet")

    with pytest.raises(CatalogCacheError):
        load_catalog_db("FM01", cache_dir=tmp_path, client=client)


def test_load_catalog_all_merges_requested_dbs(tmp_path: Path) -> None:
    client = Mock(spec=httpx.Client)
    client.get.side_effect = [
        _mock_response(_parquet_bytes([{"series_code": "FM_CODE"}])),
        _mock_response(_parquet_bytes([{"series_code": "BP_CODE"}])),
    ]

    table = load_catalog_all(
        dbs=["FM01", "BP01"],
        cache_dir=tmp_path,
        client=client,
    )

    assert table.num_rows == 2
    assert table.column("series_code").to_pylist() == ["FM_CODE", "BP_CODE"]
    assert table.column("db").to_pylist() == ["FM01", "BP01"]
    assert client.get.call_count == 2


def test_load_catalog_all_defaults_to_list_db(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "boj_stat_search.shell.catalog.loader.list_db",
        lambda: (
            DbInfo(name="FM01", desc="desc", category="cat"),
            DbInfo(name="BP01", desc="desc", category="cat"),
        ),
    )

    client = Mock(spec=httpx.Client)
    client.get.side_effect = [
        _mock_response(_parquet_bytes([{"series_code": "FM_CODE"}])),
        _mock_response(_parquet_bytes([{"series_code": "BP_CODE"}])),
    ]

    table = load_catalog_all(cache_dir=tmp_path, client=client)

    assert table.column("db").to_pylist() == ["FM01", "BP01"]
    assert client.get.call_count == 2


def test_load_catalog_db_respects_custom_ttl_zero(tmp_path: Path) -> None:
    cache_path = tmp_path / "FM01.parquet"
    _write_cached_parquet(cache_path, [{"series_code": "OLD"}])

    client = Mock(spec=httpx.Client)
    client.get.return_value = _mock_response(_parquet_bytes([{"series_code": "NEW"}]))

    table = load_catalog_db(
        "FM01",
        cache_ttl_seconds=0,
        cache_dir=tmp_path,
        client=client,
    )

    assert table.column("series_code").to_pylist() == ["NEW"]
    client.get.assert_called_once()


def test_load_catalog_db_does_not_close_external_client(tmp_path: Path) -> None:
    client = Mock(spec=httpx.Client)
    client.get.return_value = _mock_response(_parquet_bytes([{"series_code": "A"}]))

    load_catalog_db("FM01", cache_dir=tmp_path, client=client)

    client.close.assert_not_called()


def test_load_catalog_all_reuses_one_internal_client(
    tmp_path: Path, monkeypatch
) -> None:
    internal_client = Mock(spec=httpx.Client)
    internal_client.get.side_effect = [
        _mock_response(_parquet_bytes([{"series_code": "FM_CODE"}])),
        _mock_response(_parquet_bytes([{"series_code": "BP_CODE"}])),
    ]
    factory = Mock(return_value=internal_client)
    monkeypatch.setattr("boj_stat_search.shell.catalog.loader.httpx.Client", factory)

    load_catalog_all(dbs=["FM01", "BP01"], cache_dir=tmp_path)

    factory.assert_called_once()
    assert internal_client.get.call_count == 2
    internal_client.close.assert_called_once()


def test_load_catalog_all_does_not_close_external_client(tmp_path: Path) -> None:
    client = Mock(spec=httpx.Client)
    client.get.side_effect = [
        _mock_response(_parquet_bytes([{"series_code": "FM_CODE"}])),
        _mock_response(_parquet_bytes([{"series_code": "BP_CODE"}])),
    ]

    load_catalog_all(dbs=["FM01", "BP01"], cache_dir=tmp_path, client=client)

    client.close.assert_not_called()
