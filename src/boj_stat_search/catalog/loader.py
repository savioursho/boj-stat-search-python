from __future__ import annotations

import os
import sys
import tempfile
import time
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import quote

import httpx
import pyarrow as pa
import pyarrow.parquet as pq

from boj_stat_search.core import list_db

DEFAULT_CACHE_TTL_SECONDS = 24 * 60 * 60
DEFAULT_CATALOG_REPO = "savioursho/boj-stat-search-python"
DEFAULT_CATALOG_REF = "main"
DEFAULT_METADATA_DIR = "metadata"


class CatalogError(RuntimeError):
    """Base exception for local catalog loading failures."""


class CatalogFetchError(CatalogError):
    """Raised when catalog download fails."""


class CatalogCacheError(CatalogError):
    """Raised when catalog cache read/write fails."""


def load_catalog_db(
    db: str,
    *,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    cache_dir: str | Path | None = None,
    repo: str = DEFAULT_CATALOG_REPO,
    ref: str = DEFAULT_CATALOG_REF,
    metadata_dir: str = DEFAULT_METADATA_DIR,
    client: httpx.Client | None = None,
) -> pa.Table:
    """Load one DB catalog table, fetching from GitHub raw when cache is stale."""
    if cache_ttl_seconds < 0:
        raise ValueError("cache_ttl_seconds must be >= 0")

    cache_path = _cache_file_path(db, cache_dir=cache_dir)
    should_refresh = _is_stale(cache_path, ttl_seconds=cache_ttl_seconds)

    owns_client = client is None
    http_client = client if client is not None else httpx.Client()

    try:
        if should_refresh:
            _refresh_cache(
                db=db,
                cache_path=cache_path,
                repo=repo,
                ref=ref,
                metadata_dir=metadata_dir,
                client=http_client,
            )
            return _read_catalog_table(cache_path, db=db)

        try:
            return _read_catalog_table(cache_path, db=db)
        except CatalogCacheError:
            # Recover from a corrupted but "fresh" file by forcing one re-download.
            _refresh_cache(
                db=db,
                cache_path=cache_path,
                repo=repo,
                ref=ref,
                metadata_dir=metadata_dir,
                client=http_client,
            )
            return _read_catalog_table(cache_path, db=db)
    finally:
        if owns_client:
            http_client.close()


def load_catalog_all(
    *,
    dbs: Sequence[str] | None = None,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    cache_dir: str | Path | None = None,
    repo: str = DEFAULT_CATALOG_REPO,
    ref: str = DEFAULT_CATALOG_REF,
    metadata_dir: str = DEFAULT_METADATA_DIR,
    client: httpx.Client | None = None,
) -> pa.Table:
    """Load and concatenate catalog tables for all (or selected) DBs."""
    resolved_dbs = _resolve_dbs(dbs)
    if not resolved_dbs:
        return pa.table({})

    owns_client = client is None
    http_client = client if client is not None else httpx.Client()

    try:
        tables = [
            load_catalog_db(
                db,
                cache_ttl_seconds=cache_ttl_seconds,
                cache_dir=cache_dir,
                repo=repo,
                ref=ref,
                metadata_dir=metadata_dir,
                client=http_client,
            )
            for db in resolved_dbs
        ]
    finally:
        if owns_client:
            http_client.close()

    if len(tables) == 1:
        return tables[0]

    try:
        return pa.concat_tables(tables, promote_options="default")
    except Exception as exc:
        raise CatalogCacheError(
            f"Failed to concatenate catalog tables for DBs: {', '.join(resolved_dbs)}"
        ) from exc


def _resolve_dbs(dbs: Sequence[str] | None) -> tuple[str, ...]:
    if dbs is None:
        return tuple(db_info.name for db_info in list_db())

    # Keep caller-specified order while removing duplicates.
    return tuple(dict.fromkeys(dbs))


def _refresh_cache(
    *,
    db: str,
    cache_path: Path,
    repo: str,
    ref: str,
    metadata_dir: str,
    client: httpx.Client,
) -> None:
    url = _build_raw_url(repo=repo, ref=ref, db=db, metadata_dir=metadata_dir)
    content = _download_parquet(url, client=client)

    try:
        _atomic_write_bytes(cache_path, content)
    except OSError as exc:
        raise CatalogCacheError(
            f"Failed to write catalog cache file for {db} at {cache_path}"
        ) from exc


def _read_catalog_table(cache_path: Path, *, db: str) -> pa.Table:
    try:
        table = pq.read_table(cache_path)
    except Exception as exc:
        raise CatalogCacheError(
            f"Failed to read catalog cache file for {db} at {cache_path}"
        ) from exc

    if "db" in table.column_names:
        return table

    db_column = pa.array([db] * table.num_rows, type=pa.string())
    return table.append_column("db", db_column)


def _download_parquet(url: str, *, client: httpx.Client) -> bytes:
    try:
        response = client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise CatalogFetchError(f"Failed to download catalog data from {url}") from exc

    if not response.content:
        raise CatalogFetchError(f"Catalog response is empty for {url}")

    return response.content


def _cache_file_path(db: str, *, cache_dir: str | Path | None) -> Path:
    return _cache_root(cache_dir) / f"{db}.parquet"


def _cache_root(cache_dir: str | Path | None) -> Path:
    if cache_dir is not None:
        return Path(cache_dir).expanduser()
    return _default_cache_root()


def _default_cache_root() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache"))
    return base / "boj-stat-search" / "catalog"


def _is_stale(path: Path, *, ttl_seconds: int, now: float | None = None) -> bool:
    if not path.exists():
        return True
    if ttl_seconds == 0:
        return True
    now_time = now if now is not None else time.time()
    return now_time - path.stat().st_mtime > ttl_seconds


def _build_raw_url(*, repo: str, ref: str, db: str, metadata_dir: str) -> str:
    metadata_path = metadata_dir.strip("/")
    encoded_db = quote(db, safe="")
    return (
        f"https://raw.githubusercontent.com/{repo}/{ref}/"
        f"{metadata_path}/{encoded_db}.parquet"
    )


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(content)

        if temp_path is None:
            raise RuntimeError("Failed to create temporary catalog cache file")

        temp_path.replace(path)
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        raise
