from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx
import pyarrow as pa

from boj_stat_search.catalog.loader import (
    DEFAULT_CACHE_TTL_SECONDS,
    DEFAULT_CATALOG_REF,
    DEFAULT_CATALOG_REPO,
    DEFAULT_METADATA_DIR,
    CatalogError,
    load_catalog_all,
    load_catalog_db,
)
from boj_stat_search.core import Layer, list_db
from boj_stat_search.core.validator import coerce_layer
from boj_stat_search.models import SeriesCatalogEntry

_SEARCH_FIELDS: tuple[str, ...] = ("name_j", "name_en", "category_j", "category_en")
_REQUIRED_COLUMNS: tuple[str, ...] = (
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


def search_series(
    keyword: str,
    *,
    db: str | None = None,
    dbs: Sequence[str] | None = None,
    layer: Layer | str | None = None,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    cache_dir: str | Path | None = None,
    repo: str = DEFAULT_CATALOG_REPO,
    ref: str = DEFAULT_CATALOG_REF,
    metadata_dir: str = DEFAULT_METADATA_DIR,
    client: httpx.Client | None = None,
) -> tuple[SeriesCatalogEntry, ...]:
    """Search local metadata catalog entries by keyword."""
    normalized_keyword = _normalize_keyword(keyword)
    known_dbs = {db_info.name for db_info in list_db()}
    resolved_dbs = _resolve_dbs(db=db, dbs=dbs, known_dbs=known_dbs)
    layer_parts = _coerce_and_validate_layer(layer)

    if resolved_dbs is not None and len(resolved_dbs) == 0:
        return ()

    if resolved_dbs is None:
        table = load_catalog_all(
            cache_ttl_seconds=cache_ttl_seconds,
            cache_dir=cache_dir,
            repo=repo,
            ref=ref,
            metadata_dir=metadata_dir,
            client=client,
        )
    elif len(resolved_dbs) == 1:
        table = load_catalog_db(
            resolved_dbs[0],
            cache_ttl_seconds=cache_ttl_seconds,
            cache_dir=cache_dir,
            repo=repo,
            ref=ref,
            metadata_dir=metadata_dir,
            client=client,
        )
    else:
        table = load_catalog_all(
            dbs=resolved_dbs,
            cache_ttl_seconds=cache_ttl_seconds,
            cache_dir=cache_dir,
            repo=repo,
            ref=ref,
            metadata_dir=metadata_dir,
            client=client,
        )

    entries = _table_to_entries(table)

    return tuple(
        entry
        for entry in entries
        if _row_matches_layer(entry, layer_parts)
        and _row_matches_keyword(entry, normalized_keyword)
    )


def list_series(
    db: str,
    *,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    cache_dir: str | Path | None = None,
    repo: str = DEFAULT_CATALOG_REPO,
    ref: str = DEFAULT_CATALOG_REF,
    metadata_dir: str = DEFAULT_METADATA_DIR,
    client: httpx.Client | None = None,
) -> tuple[SeriesCatalogEntry, ...]:
    """List all local metadata catalog entries for one DB."""
    known_dbs = {db_info.name for db_info in list_db()}
    _validate_db_name(db, known_dbs=known_dbs)

    table = load_catalog_db(
        db,
        cache_ttl_seconds=cache_ttl_seconds,
        cache_dir=cache_dir,
        repo=repo,
        ref=ref,
        metadata_dir=metadata_dir,
        client=client,
    )
    return _table_to_entries(table)


def _normalize_keyword(keyword: str) -> str:
    if not isinstance(keyword, str):
        raise ValueError("keyword: must be a string")
    normalized = keyword.strip()
    if not normalized:
        raise ValueError("keyword: must not be empty")
    return normalized.casefold()


def _resolve_dbs(
    *,
    db: str | None,
    dbs: Sequence[str] | None,
    known_dbs: set[str],
) -> tuple[str, ...] | None:
    if db is not None and dbs is not None:
        raise ValueError("db and dbs cannot both be provided")

    if db is not None:
        _validate_db_name(db, known_dbs=known_dbs)
        return (db,)

    if dbs is None:
        return None

    resolved_dbs: list[str] = []
    seen: set[str] = set()
    for name in dbs:
        if not isinstance(name, str):
            raise ValueError("dbs: each DB name must be a string")
        if name not in known_dbs:
            raise ValueError("dbs: each DB must be one of known DB names in list_db()")
        if name in seen:
            continue
        seen.add(name)
        resolved_dbs.append(name)

    return tuple(resolved_dbs)


def _validate_db_name(db: str, *, known_dbs: set[str]) -> None:
    if not isinstance(db, str):
        raise ValueError("db: must be one of known DB names in list_db()")
    if db not in known_dbs:
        raise ValueError("db: must be one of known DB names in list_db()")


def _coerce_and_validate_layer(layer: Layer | str | None) -> tuple[str, ...] | None:
    if layer is None:
        return None

    normalized = coerce_layer(layer)
    if not isinstance(normalized, str):
        raise ValueError("layer: must be a string or Layer")
    if normalized == "":
        raise ValueError("layer: must not be empty")

    parts = [part.strip() for part in normalized.split(",")]
    if len(parts) < 1 or len(parts) > 5:
        raise ValueError("layer: must have between 1 and 5 comma-separated values")
    if any(part == "" for part in parts):
        raise ValueError("layer: must not contain empty layer values")

    for part in parts:
        if part != "*" and not part.isdigit():
            raise ValueError("layer: each layer must be '*' or digits only")

    return tuple(parts)


def _row_matches_layer(
    row: SeriesCatalogEntry, layer_parts: tuple[str, ...] | None
) -> bool:
    if layer_parts is None:
        return True

    row_layers = (
        str(row.layer1),
        str(row.layer2),
        str(row.layer3),
        str(row.layer4),
        str(row.layer5),
    )

    for index, expected in enumerate(layer_parts):
        if expected == "*":
            continue
        if row_layers[index] != expected:
            return False

    return True


def _row_matches_keyword(row: SeriesCatalogEntry, normalized_keyword: str) -> bool:
    for field in _SEARCH_FIELDS:
        value = getattr(row, field)
        if normalized_keyword in value.casefold():
            return True
    return False


def _table_to_entries(table: pa.Table) -> tuple[SeriesCatalogEntry, ...]:
    _ensure_required_columns(table.column_names)

    entries: list[SeriesCatalogEntry] = []
    for row in table.to_pylist():
        entries.append(_row_to_entry(row))
    return tuple(entries)


def _ensure_required_columns(column_names: list[str]) -> None:
    missing = [column for column in _REQUIRED_COLUMNS if column not in column_names]
    if missing:
        raise CatalogError(
            "Catalog table is missing required columns: " + ", ".join(missing)
        )


def _row_to_entry(row: dict[str, Any]) -> SeriesCatalogEntry:
    try:
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
    except ValueError as exc:
        raise CatalogError("Catalog row contains invalid values") from exc


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
