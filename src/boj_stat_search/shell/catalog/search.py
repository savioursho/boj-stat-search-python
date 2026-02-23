from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import httpx
import pyarrow as pa
import pyarrow.parquet as pq

from boj_stat_search.shell.catalog.loader import (
    DEFAULT_CACHE_TTL_SECONDS,
    DEFAULT_CATALOG_REF,
    DEFAULT_CATALOG_REPO,
    DEFAULT_METADATA_DIR,
    _cache_file_path,
    CatalogError,
    load_catalog_all,
    load_catalog_db,
)
from boj_stat_search.core import (
    Layer,
    list_db,
    table_to_entries as _core_table_to_entries,
)
from boj_stat_search.core.validator import coerce_layer
from boj_stat_search.core.models import SeriesCatalogEntry

_SEARCH_FIELDS: tuple[str, ...] = ("name_j", "name_en", "category_j", "category_en")


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


def resolve_db(
    series_code: str,
    *,
    cache_dir: str | Path | None = None,
) -> str:
    """Resolve DB for a series code using local cached catalog parquet files only."""
    if not isinstance(series_code, str):
        raise ValueError("series_code: must be a non-empty string")
    normalized_series_code = series_code.strip()
    if normalized_series_code == "":
        raise ValueError("series_code: must be a non-empty string")

    matched_dbs: list[str] = []
    for db_info in list_db():
        db_name = db_info.name
        cache_path = _cache_file_path(db_name, cache_dir=cache_dir)
        if not cache_path.exists():
            continue

        table = pq.read_table(cache_path)
        if "series_code" not in table.column_names:
            continue

        match_mask = pa.array(
            [
                value == normalized_series_code
                for value in table["series_code"].to_pylist()
            ]
        )
        matched = table.filter(match_mask)
        if matched.num_rows > 0:
            matched_dbs.append(db_name)

    if len(matched_dbs) == 1:
        return matched_dbs[0]
    if len(matched_dbs) == 0:
        raise ValueError(
            "resolve_db: series code not found in any cached catalog; "
            "specify db explicitly or run load_catalog_all() to populate cache"
        )
    raise ValueError(
        "resolve_db: series code found in multiple DBs; specify db explicitly"
    )


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
    try:
        return _core_table_to_entries(table)
    except ValueError as exc:
        raise CatalogError(str(exc)) from exc
