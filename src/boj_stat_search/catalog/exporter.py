from __future__ import annotations

import csv
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from boj_stat_search.client import BojClient
from boj_stat_search.core import list_db
from boj_stat_search.models import MetadataEntry

METADATA_CSV_COLUMNS: tuple[str, ...] = (
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
                "db": db,
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
            }
        )

    return rows


def write_metadata_csv(
    file_path: str | Path,
    rows: Sequence[Mapping[str, str | int]],
) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            writer = csv.DictWriter(temp_file, fieldnames=list(METADATA_CSV_COLUMNS))
            writer.writeheader()
            writer.writerows(rows)

        if temp_path is None:
            raise RuntimeError("Failed to create temporary metadata CSV file")

        temp_path.replace(path)
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        raise


def generate_metadata_csvs(
    output_dir: str | Path = "metadata",
    dbs: Sequence[str] | None = None,
    min_request_interval: float = 1.0,
) -> MetadataExportReport:
    output_dir_path = Path(output_dir)
    requested_dbs = _resolve_dbs(dbs)

    succeeded_dbs: list[str] = []
    row_counts: dict[str, int] = {}
    error_messages: dict[str, str] = {}

    with BojClient(min_request_interval=min_request_interval) as client:
        for db in requested_dbs:
            try:
                metadata = client.get_metadata(db)
                rows = metadata_entries_to_rows(db, metadata.result_set)
                write_metadata_csv(output_dir_path / f"{db}.csv", rows)
            except Exception as exc:
                error_messages[db] = str(exc)
                continue

            succeeded_dbs.append(db)
            row_counts[db] = len(rows)

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
