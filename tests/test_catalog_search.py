from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import httpx
import pyarrow as pa
import pytest

from boj_stat_search.catalog import CatalogError, search_series
from boj_stat_search.core import Layer
from boj_stat_search.models import SeriesCatalogEntry


def _make_row(
    *,
    db: str,
    series_code: str,
    name_j: str,
    name_en: str,
    category_j: str = "カテゴリ",
    category_en: str = "Category",
    layer1: int = 1,
    layer2: int = 0,
    layer3: int = 0,
    layer4: int = 0,
    layer5: int = 0,
) -> dict[str, str | int]:
    return {
        "db": db,
        "series_code": series_code,
        "name_j": name_j,
        "name_en": name_en,
        "unit_j": "unit-j",
        "unit_en": "unit-en",
        "frequency": "M",
        "category_j": category_j,
        "category_en": category_en,
        "layer1": layer1,
        "layer2": layer2,
        "layer3": layer3,
        "layer4": layer4,
        "layer5": layer5,
        "start_of_time_series": "199901",
        "end_of_time_series": "202601",
        "last_update": "20260222",
        "notes_j": "",
        "notes_en": "",
    }


def _table(rows: list[dict[str, str | int]]) -> pa.Table:
    return pa.Table.from_pylist(rows)


def test_search_series_matches_japanese_keyword(monkeypatch) -> None:
    monkeypatch.setattr(
        "boj_stat_search.catalog.search.load_catalog_all",
        lambda **_: _table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="対米ドル為替レート",
                    name_en="USD/JPY",
                ),
                _make_row(
                    db="BP01",
                    series_code="BP01'B",
                    name_j="マネーストック",
                    name_en="Money Stock",
                ),
            ]
        ),
    )

    results = search_series("為替")

    assert tuple(entry.series_code for entry in results) == ("FM01'A",)
    assert isinstance(results[0], SeriesCatalogEntry)


def test_search_series_matches_english_keyword_case_insensitive(monkeypatch) -> None:
    monkeypatch.setattr(
        "boj_stat_search.catalog.search.load_catalog_all",
        lambda **_: _table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="対米ドル為替レート",
                    name_en="Exchange Rate",
                ),
                _make_row(
                    db="FM01",
                    series_code="FM01'B",
                    name_j="無担保コール",
                    name_en="Call Rate",
                ),
            ]
        ),
    )

    results = search_series("eXcHaNgE")

    assert tuple(entry.series_code for entry in results) == ("FM01'A",)


def test_search_series_matches_category_fields(monkeypatch) -> None:
    monkeypatch.setattr(
        "boj_stat_search.catalog.search.load_catalog_all",
        lambda **_: _table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="無担保コール",
                    name_en="Call Rate",
                    category_j="金融市場",
                    category_en="Financial Markets",
                ),
                _make_row(
                    db="BP01",
                    series_code="BP01'B",
                    name_j="マネーストック",
                    name_en="Money Stock",
                    category_j="通貨",
                    category_en="Money",
                ),
            ]
        ),
    )

    results = search_series("financial")

    assert tuple(entry.series_code for entry in results) == ("FM01'A",)


def test_search_series_with_db_uses_load_catalog_db(monkeypatch) -> None:
    load_db = Mock(
        return_value=_table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="無担保コール",
                    name_en="Call Rate",
                )
            ]
        )
    )
    load_all = Mock()
    monkeypatch.setattr("boj_stat_search.catalog.search.load_catalog_db", load_db)
    monkeypatch.setattr("boj_stat_search.catalog.search.load_catalog_all", load_all)

    results = search_series("call", db="FM01")

    assert tuple(entry.series_code for entry in results) == ("FM01'A",)
    load_db.assert_called_once()
    load_all.assert_not_called()


def test_search_series_with_dbs_uses_load_catalog_all(monkeypatch) -> None:
    load_all = Mock(
        return_value=_table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="無担保コール",
                    name_en="Call Rate",
                ),
                _make_row(
                    db="BP01",
                    series_code="BP01'B",
                    name_j="マネーストック",
                    name_en="Money Stock",
                ),
            ]
        )
    )
    load_db = Mock()
    monkeypatch.setattr("boj_stat_search.catalog.search.load_catalog_all", load_all)
    monkeypatch.setattr("boj_stat_search.catalog.search.load_catalog_db", load_db)

    results = search_series("rate", dbs=["FM01", "BP01", "FM01"])

    assert tuple(entry.series_code for entry in results) == ("FM01'A",)
    load_all.assert_called_once()
    assert load_all.call_args.kwargs["dbs"] == ("FM01", "BP01")
    load_db.assert_not_called()


def test_search_series_rejects_db_and_dbs_together() -> None:
    with pytest.raises(ValueError, match="cannot both be provided"):
        search_series("rate", db="FM01", dbs=["FM01"])


def test_search_series_returns_empty_for_empty_dbs(monkeypatch) -> None:
    load_all = Mock()
    load_db = Mock()
    monkeypatch.setattr("boj_stat_search.catalog.search.load_catalog_all", load_all)
    monkeypatch.setattr("boj_stat_search.catalog.search.load_catalog_db", load_db)

    results = search_series("rate", dbs=[])

    assert results == ()
    load_all.assert_not_called()
    load_db.assert_not_called()


def test_search_series_rejects_unknown_db() -> None:
    with pytest.raises(ValueError, match="list_db"):
        search_series("rate", db="UNKNOWN")


def test_search_series_filters_by_layer_prefix_and_wildcard(monkeypatch) -> None:
    monkeypatch.setattr(
        "boj_stat_search.catalog.search.load_catalog_all",
        lambda **_: _table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="A",
                    name_en="Rate A",
                    layer1=1,
                    layer2=2,
                    layer3=3,
                ),
                _make_row(
                    db="FM01",
                    series_code="FM01'B",
                    name_j="B",
                    name_en="Rate B",
                    layer1=1,
                    layer2=9,
                    layer3=3,
                ),
                _make_row(
                    db="FM01",
                    series_code="FM01'C",
                    name_j="C",
                    name_en="Rate C",
                    layer1=2,
                    layer2=2,
                    layer3=3,
                ),
            ]
        ),
    )

    results = search_series("rate", layer="1,*,3")

    assert tuple(entry.series_code for entry in results) == ("FM01'A", "FM01'B")


def test_search_series_accepts_layer_object(monkeypatch) -> None:
    monkeypatch.setattr(
        "boj_stat_search.catalog.search.load_catalog_all",
        lambda **_: _table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="A",
                    name_en="Rate A",
                    layer1=1,
                    layer2=2,
                    layer3=3,
                ),
                _make_row(
                    db="FM01",
                    series_code="FM01'B",
                    name_j="B",
                    name_en="Rate B",
                    layer1=1,
                    layer2=2,
                    layer3=4,
                ),
            ]
        ),
    )

    results = search_series("rate", layer=Layer(1, "*", 3))

    assert tuple(entry.series_code for entry in results) == ("FM01'A",)


def test_search_series_rejects_invalid_layer() -> None:
    with pytest.raises(ValueError, match="digits only"):
        search_series("rate", layer="1,a")


def test_search_series_rejects_empty_keyword() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        search_series("   ")


def test_search_series_forwards_cache_and_client_options(monkeypatch) -> None:
    load_db = Mock(
        return_value=_table(
            [
                _make_row(
                    db="FM01",
                    series_code="FM01'A",
                    name_j="無担保コール",
                    name_en="Call Rate",
                )
            ]
        )
    )
    monkeypatch.setattr("boj_stat_search.catalog.search.load_catalog_db", load_db)

    client = Mock(spec=httpx.Client)
    cache_dir = Path("/tmp/catalog-cache")
    search_series(
        "call",
        db="FM01",
        cache_ttl_seconds=60,
        cache_dir=cache_dir,
        repo="owner/repo",
        ref="develop",
        metadata_dir="metadata",
        client=client,
    )

    load_db.assert_called_once_with(
        "FM01",
        cache_ttl_seconds=60,
        cache_dir=cache_dir,
        repo="owner/repo",
        ref="develop",
        metadata_dir="metadata",
        client=client,
    )


def test_search_series_raises_catalog_error_when_columns_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        "boj_stat_search.catalog.search.load_catalog_all",
        lambda **_: pa.table({"series_code": ["FM01'A"]}),
    )

    with pytest.raises(CatalogError, match="missing required columns"):
        search_series("fm01")
