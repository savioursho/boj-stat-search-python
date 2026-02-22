from __future__ import annotations

import tempfile
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm

from boj_stat_search.client import BojClient
from boj_stat_search.core import list_db
from boj_stat_search.models import MetadataEntry

METADATA_PARQUET_COLUMNS: tuple[str, ...] = (
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

METADATA_PARQUET_SCHEMA = pa.schema(
    [
        pa.field("series_code", pa.string()),
        pa.field("name_j", pa.string()),
        pa.field("name_en", pa.string()),
        pa.field("unit_j", pa.string()),
        pa.field("unit_en", pa.string()),
        pa.field("frequency", pa.string()),
        pa.field("category_j", pa.string()),
        pa.field("category_en", pa.string()),
        pa.field("layer1", pa.int64()),
        pa.field("layer2", pa.int64()),
        pa.field("layer3", pa.int64()),
        pa.field("layer4", pa.int64()),
        pa.field("layer5", pa.int64()),
        pa.field("start_of_time_series", pa.string()),
        pa.field("end_of_time_series", pa.string()),
        pa.field("last_update", pa.string()),
        pa.field("notes_j", pa.string()),
        pa.field("notes_en", pa.string()),
    ]
)


@dataclass(frozen=True)
class MetadataExportReport:
    output_dir: Path
    requested_dbs: tuple[str, ...]
    succeeded_dbs: tuple[str, ...]
    failed_dbs: tuple[str, ...]
    row_counts: Mapping[str, int]
    error_messages: Mapping[str, str]

    @property
    def total_dbs(self) -> int:
        return len(self.requested_dbs)

    @property
    def succeeded_count(self) -> int:
        return len(self.succeeded_dbs)

    @property
    def failed_count(self) -> int:
        return len(self.failed_dbs)

    @property
    def is_success(self) -> bool:
        return self.failed_count == 0


def metadata_entries_to_rows(
    db: str,
    entries: Iterable[MetadataEntry],
) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []

    for entry in entries:
        if not entry.series_code.strip():
            continue

        rows.append(
            {
                "series_code": entry.series_code,
                "name_j": entry.name_of_time_series_j,
                "name_en": entry.name_of_time_series,
                "unit_j": entry.unit_j,
                "unit_en": entry.unit,
                "frequency": entry.frequency,
                "category_j": entry.category_j,
                "category_en": entry.category,
                "layer1": entry.layer1,
                "layer2": entry.layer2,
                "layer3": entry.layer3,
                "layer4": entry.layer4,
                "layer5": entry.layer5,
                "start_of_time_series": entry.start_of_the_time_series,
                "end_of_time_series": entry.end_of_the_time_series,
                "last_update": entry.last_update,
                "notes_j": entry.notes_j,
                "notes_en": entry.notes,
            }
        )

    return rows


def write_metadata_parquet(
    file_path: str | Path,
    rows: Sequence[Mapping[str, str | int]],
) -> None:
    path = Path(file_path)
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
            table = pa.Table.from_pylist(list(rows), schema=METADATA_PARQUET_SCHEMA)
            pq.write_table(table, temp_file, compression="snappy")

        if temp_path is None:
            raise RuntimeError("Failed to create temporary metadata Parquet file")

        temp_path.replace(path)
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        raise


def generate_metadata_parquet_files(
    output_dir: str | Path = "metadata",
    dbs: Sequence[str] | None = None,
    min_request_interval: float = 1.0,
    *,
    show_progress: bool = False,
) -> MetadataExportReport:
    output_dir_path = Path(output_dir)
    requested_dbs = _resolve_dbs(dbs)

    succeeded_dbs: list[str] = []
    row_counts: dict[str, int] = {}
    error_messages: dict[str, str] = {}

    progress = tqdm(
        total=len(requested_dbs),
        desc="Generating metadata Parquet",
        unit="db",
        disable=not show_progress,
    )
    try:
        with BojClient(min_request_interval=min_request_interval) as client:
            for db in requested_dbs:
                try:
                    metadata = client.get_metadata(db)
                    rows = metadata_entries_to_rows(db, metadata.result_set)
                    write_metadata_parquet(output_dir_path / f"{db}.parquet", rows)
                except Exception as exc:
                    error_messages[db] = str(exc)
                    progress.set_postfix_str(f"{db}: failed")
                    progress.update(1)
                    continue

                succeeded_dbs.append(db)
                row_counts[db] = len(rows)
                progress.set_postfix_str(f"{db}: {len(rows)} rows")
                progress.update(1)
    finally:
        progress.close()

    failed_dbs = tuple(db for db in requested_dbs if db in error_messages)

    return MetadataExportReport(
        output_dir=output_dir_path,
        requested_dbs=requested_dbs,
        succeeded_dbs=tuple(succeeded_dbs),
        failed_dbs=failed_dbs,
        row_counts=MappingProxyType(row_counts),
        error_messages=MappingProxyType(error_messages),
    )


def _resolve_dbs(dbs: Sequence[str] | None) -> tuple[str, ...]:
    if dbs is None:
        return tuple(db_info.name for db_info in list_db())

    # Keep caller-specified order while removing duplicates.
    return tuple(dict.fromkeys(dbs))
