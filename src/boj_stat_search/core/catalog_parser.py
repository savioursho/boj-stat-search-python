from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pyarrow as pa

from boj_stat_search.core.models import SeriesCatalogEntry

REQUIRED_COLUMNS: tuple[str, ...] = (
    "db",
    "series_code",
    "name_j",
    "name_en",
    "unit_j",
    "unit_en",
    "frequency",
    "category_j",
    "category_en",
    "layer1",
    "layer2",
    "layer3",
    "layer4",
    "layer5",
    "start_of_time_series",
    "end_of_time_series",
    "last_update",
    "notes_j",
    "notes_en",
)


def table_to_entries(table: pa.Table) -> tuple[SeriesCatalogEntry, ...]:
    ensure_required_columns(table.column_names)

    entries: list[SeriesCatalogEntry] = []
    for row in table.to_pylist():
        entries.append(row_to_entry(row))
    return tuple(entries)


def ensure_required_columns(column_names: list[str]) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in column_names]
    if missing:
        raise ValueError(
            "Catalog table is missing required columns: " + ", ".join(missing)
        )


def row_to_entry(row: dict[str, Any]) -> SeriesCatalogEntry:
    return SeriesCatalogEntry(
        db=_required_str(row, "db"),
        series_code=_required_str(row, "series_code"),
        name_j=_required_str(row, "name_j"),
        name_en=_required_str(row, "name_en"),
        unit_j=_required_str(row, "unit_j"),
        unit_en=_required_str(row, "unit_en"),
        frequency=_required_str(row, "frequency"),
        category_j=_required_str(row, "category_j"),
        category_en=_required_str(row, "category_en"),
        layer1=_required_int(row, "layer1"),
        layer2=_required_int(row, "layer2"),
        layer3=_required_int(row, "layer3"),
        layer4=_required_int(row, "layer4"),
        layer5=_required_int(row, "layer5"),
        start_of_time_series=_required_str(row, "start_of_time_series"),
        end_of_time_series=_required_str(row, "end_of_time_series"),
        last_update=_required_str(row, "last_update"),
        notes_j=_required_str(row, "notes_j"),
        notes_en=_required_str(row, "notes_en"),
    )


def _required_str(row: dict[str, Any], field: str) -> str:
    value = row[field]
    if not isinstance(value, str):
        raise ValueError(f"{field}: must be a string")
    return value


def _required_int(row: dict[str, Any], field: str) -> int:
    value = row[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field}: must be an integer")
    return value


def resolve_db_from_tables(
    series_code: str,
    tables: Sequence[tuple[str, pa.Table]],
) -> str:
    matched_dbs: list[str] = []
    for db_name, table in tables:
        match_mask = pa.array(
            [value == series_code for value in table["series_code"].to_pylist()]
        )
        matched = table.filter(match_mask)
        if matched.num_rows > 0:
            matched_dbs.append(db_name)

    if len(matched_dbs) == 1:
        return matched_dbs[0]
    if len(matched_dbs) == 0:
        raise ValueError(
            "resolve_db_from_tables: series code not found in any cached catalog; "
            "specify db explicitly or run load_catalog_all() to populate cache"
        )
    raise ValueError(
        "resolve_db_from_tables: series code found in multiple DBs; specify db explicitly"
    )
