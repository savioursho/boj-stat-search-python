from __future__ import annotations

import pyarrow as pa
import pytest

from boj_stat_search.core.catalog_parser import (
    ensure_required_columns,
    row_to_entry,
    table_to_entries,
    REQUIRED_COLUMNS,
)
from boj_stat_search.core.models import SeriesCatalogEntry


def _make_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "db": "BS",
        "series_code": "BS01'MABJMBS_MA_C__CM_S111",
        "name_j": "テスト",
        "name_en": "Test",
        "unit_j": "百万円",
        "unit_en": "million yen",
        "frequency": "Monthly",
        "category_j": "カテゴリ",
        "category_en": "Category",
        "layer1": 1,
        "layer2": 2,
        "layer3": 3,
        "layer4": 4,
        "layer5": 5,
        "start_of_time_series": "2000-01",
        "end_of_time_series": "2024-12",
        "last_update": "2025-01-01",
        "notes_j": "備考",
        "notes_en": "Notes",
    }
    base.update(overrides)
    return base


def _make_table(rows: list[dict[str, object]] | None = None) -> pa.Table:
    if rows is None:
        rows = [_make_row()]
    if not rows:
        schema = pa.schema([(col, pa.string()) for col in REQUIRED_COLUMNS])
        return pa.table(
            {col: pa.array([], type=pa.string()) for col in REQUIRED_COLUMNS},
            schema=schema,
        )
    keys = list(rows[0].keys())
    data = {k: [row[k] for row in rows] for k in keys}
    return pa.table(data)


# ---------------------------------------------------------------------------
# ensure_required_columns
# ---------------------------------------------------------------------------


def test_ensure_required_columns_passes_with_all_columns() -> None:
    ensure_required_columns(list(REQUIRED_COLUMNS))


def test_ensure_required_columns_passes_with_extra_columns() -> None:
    cols = list(REQUIRED_COLUMNS) + ["extra"]
    ensure_required_columns(cols)


def test_ensure_required_columns_raises_when_column_missing() -> None:
    cols = [c for c in REQUIRED_COLUMNS if c != "db"]
    with pytest.raises(ValueError, match="db"):
        ensure_required_columns(cols)


def test_ensure_required_columns_error_includes_all_missing() -> None:
    cols = [c for c in REQUIRED_COLUMNS if c not in ("db", "series_code")]
    with pytest.raises(ValueError) as exc_info:
        ensure_required_columns(cols)
    msg = str(exc_info.value)
    assert "db" in msg
    assert "series_code" in msg


# ---------------------------------------------------------------------------
# row_to_entry
# ---------------------------------------------------------------------------


def test_row_to_entry_returns_correct_entry() -> None:
    row = _make_row()
    entry = row_to_entry(row)
    assert isinstance(entry, SeriesCatalogEntry)
    assert entry.db == "BS"
    assert entry.layer1 == 1
    assert entry.layer5 == 5
    assert entry.name_en == "Test"


def test_row_to_entry_raises_on_non_string_field() -> None:
    row = _make_row(name_j=123)
    with pytest.raises(ValueError, match="name_j"):
        row_to_entry(row)

def test_row_to_entry_raises_on_non_int_layer() -> None:
    row = _make_row(layer1="one")
    with pytest.raises(ValueError, match="layer1"):
        row_to_entry(row)

def test_row_to_entry_raises_on_bool_layer() -> None:
    row = _make_row(layer1=True)
    with pytest.raises(ValueError, match="layer1"):
        row_to_entry(row)

# ---------------------------------------------------------------------------
# table_to_entries
# ---------------------------------------------------------------------------


def test_table_to_entries_converts_multi_row_table() -> None:
    rows = [_make_row(series_code=f"CODE{i}") for i in range(3)]
    table = _make_table(rows)
    entries = table_to_entries(table)
    assert len(entries) == 3
    assert all(isinstance(e, SeriesCatalogEntry) for e in entries)
    assert {e.series_code for e in entries} == {"CODE0", "CODE1", "CODE2"}


def test_table_to_entries_empty_table_returns_empty_tuple() -> None:
    table = _make_table([])
    entries = table_to_entries(table)
    assert entries == ()


def test_table_to_entries_raises_on_missing_columns() -> None:
    table = pa.table({"db": ["BS"], "series_code": ["X"]})
    with pytest.raises(ValueError, match="missing required columns"):
        table_to_entries(table)


def test_table_to_entries_raises_on_invalid_row_data() -> None:
    rows = [_make_row(layer1="bad")]
    table = _make_table(rows)
    with pytest.raises(ValueError, match="layer1"):
        table_to_entries(table)
