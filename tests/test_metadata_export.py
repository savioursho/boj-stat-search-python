from __future__ import annotations

from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from boj_stat_search.catalog import (
    METADATA_PARQUET_COLUMNS,
    generate_metadata_parquet_files,
    metadata_entries_to_rows,
    write_metadata_parquet,
)
from boj_stat_search.models import MetadataEntry, MetadataResponse


def _make_entry(
    series_code: str,
    *,
    name_j: str = "name-j",
    name_en: str = "name-en",
    notes_j: str = "",
    notes_en: str = "",
) -> MetadataEntry:
    return MetadataEntry(
        series_code=series_code,
        name_of_time_series_j=name_j,
        name_of_time_series=name_en,
        unit_j="unit-j",
        unit="unit-en",
        frequency="M",
        category_j="cat-j",
        category="cat-en",
        layer1=1,
        layer2=2,
        layer3=3,
        layer4=4,
        layer5=5,
        start_of_the_time_series="199901",
        end_of_the_time_series="202601",
        last_update="20260222",
        notes_j=notes_j,
        notes=notes_en,
    )


def _make_metadata_response(
    db: str, entries: tuple[MetadataEntry, ...]
) -> MetadataResponse:
    return MetadataResponse(
        status=200,
        message_id="M181000I",
        message="ok",
        date="2026-02-22T00:00:00+09:00",
        db=db,
        result_set=entries,
    )


def test_metadata_entries_to_rows_filters_empty_series_code_and_maps_fields() -> None:
    rows = metadata_entries_to_rows(
        "FM01",
        (
            _make_entry(""),
            _make_entry(
                "STRDCLUCON",
                name_j="無担保コール",
                name_en="Call Rate",
                notes_j="備考",
                notes_en="note",
            ),
        ),
    )

    assert rows == [
        {
            "series_code": "STRDCLUCON",
            "name_j": "無担保コール",
            "name_en": "Call Rate",
            "unit_j": "unit-j",
            "unit_en": "unit-en",
            "frequency": "M",
            "category_j": "cat-j",
            "category_en": "cat-en",
            "layer1": 1,
            "layer2": 2,
            "layer3": 3,
            "layer4": 4,
            "layer5": 5,
            "start_of_time_series": "199901",
            "end_of_time_series": "202601",
            "last_update": "20260222",
            "notes_j": "備考",
            "notes_en": "note",
        }
    ]


def test_write_metadata_parquet_writes_expected_schema_and_rows(tmp_path: Path) -> None:
    rows = [
        {
            "series_code": "STRDCLUCON",
            "name_j": "name-j",
            "name_en": "name-en",
            "unit_j": "unit-j",
            "unit_en": "unit-en",
            "frequency": "M",
            "category_j": "cat-j",
            "category_en": "cat-en",
            "layer1": 1,
            "layer2": 2,
            "layer3": 3,
            "layer4": 4,
            "layer5": 5,
            "start_of_time_series": "199901",
            "end_of_time_series": "202601",
            "last_update": "20260222",
            "notes_j": "notes-j",
            "notes_en": "notes-en",
        }
    ]
    output = tmp_path / "metadata" / "FM01.parquet"

    write_metadata_parquet(output, rows)

    table = pq.read_table(output)
    assert table.column_names == list(METADATA_PARQUET_COLUMNS)
    parsed_rows = table.to_pylist()
    assert parsed_rows == rows


class _FakeClient:
    def __init__(
        self, responses: dict[str, Any], *, min_request_interval: float
    ) -> None:
        self._responses = responses
        self.min_request_interval = min_request_interval
        self.calls: list[str] = []

    def __enter__(self) -> "_FakeClient":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def get_metadata(self, db: str) -> MetadataResponse:
        self.calls.append(db)
        response = self._responses[db]
        if isinstance(response, Exception):
            raise response
        return response


def test_generate_metadata_parquet_files_writes_files_and_is_idempotent(
    tmp_path: Path,
    monkeypatch,
) -> None:
    responses: dict[str, Any] = {
        "FM01": _make_metadata_response("FM01", (_make_entry("STRDCLUCON"),)),
        "BP01": _make_metadata_response(
            "BP01",
            (
                _make_entry("CODE1"),
                _make_entry("CODE2"),
                _make_entry(""),
            ),
        ),
    }

    created_clients: list[_FakeClient] = []

    def fake_client_factory(*, min_request_interval: float) -> _FakeClient:
        client = _FakeClient(responses, min_request_interval=min_request_interval)
        created_clients.append(client)
        return client

    monkeypatch.setattr(
        "boj_stat_search.catalog.exporter.BojClient", fake_client_factory
    )

    output_dir = tmp_path / "metadata"
    report1 = generate_metadata_parquet_files(
        output_dir=output_dir,
        dbs=["FM01", "FM01", "BP01"],
        min_request_interval=0.25,
    )

    fm01_parquet = output_dir / "FM01.parquet"
    bp01_parquet = output_dir / "BP01.parquet"
    first_fm01_rows = pq.read_table(fm01_parquet).to_pylist()
    first_bp01_rows = pq.read_table(bp01_parquet).to_pylist()

    report2 = generate_metadata_parquet_files(
        output_dir=output_dir,
        dbs=["FM01", "BP01"],
        min_request_interval=0.25,
    )

    assert report1.is_success is True
    assert report1.total_dbs == 2
    assert report1.succeeded_count == 2
    assert report1.failed_count == 0
    assert report1.requested_dbs == ("FM01", "BP01")
    assert report1.succeeded_dbs == ("FM01", "BP01")
    assert report1.failed_dbs == ()
    assert report1.row_counts["FM01"] == 1
    assert report1.row_counts["BP01"] == 2
    assert dict(report1.error_messages) == {}

    assert fm01_parquet.exists()
    assert bp01_parquet.exists()
    assert pq.read_table(fm01_parquet).column_names == list(METADATA_PARQUET_COLUMNS)
    assert pq.read_table(bp01_parquet).column_names == list(METADATA_PARQUET_COLUMNS)
    assert pq.read_table(fm01_parquet).to_pylist() == first_fm01_rows
    assert pq.read_table(bp01_parquet).to_pylist() == first_bp01_rows
    assert report2.is_success is True

    assert len(created_clients) == 2
    assert created_clients[0].min_request_interval == 0.25
    assert created_clients[0].calls == ["FM01", "BP01"]


def test_generate_metadata_parquet_files_continues_on_failures_and_reports_them(
    tmp_path: Path,
    monkeypatch,
) -> None:
    responses: dict[str, Any] = {
        "FM01": _make_metadata_response("FM01", (_make_entry("STRDCLUCON"),)),
        "BP01": RuntimeError("boom"),
    }

    def fake_client_factory(*, min_request_interval: float) -> _FakeClient:
        return _FakeClient(responses, min_request_interval=min_request_interval)

    monkeypatch.setattr(
        "boj_stat_search.catalog.exporter.BojClient", fake_client_factory
    )

    output_dir = tmp_path / "metadata"
    report = generate_metadata_parquet_files(output_dir=output_dir, dbs=["FM01", "BP01"])

    assert report.is_success is False
    assert report.succeeded_dbs == ("FM01",)
    assert report.failed_dbs == ("BP01",)
    assert report.row_counts["FM01"] == 1
    assert report.error_messages["BP01"] == "boom"

    assert (output_dir / "FM01.parquet").exists()
    assert not (output_dir / "BP01.parquet").exists()


def test_generate_metadata_parquet_files_uses_tqdm_when_show_progress_enabled(
    tmp_path: Path,
    monkeypatch,
) -> None:
    responses: dict[str, Any] = {
        "FM01": _make_metadata_response("FM01", (_make_entry("STRDCLUCON"),)),
        "BP01": _make_metadata_response("BP01", (_make_entry("CODE1"),)),
    }

    def fake_client_factory(*, min_request_interval: float) -> _FakeClient:
        return _FakeClient(responses, min_request_interval=min_request_interval)

    created: dict[str, Any] = {}

    class _FakeProgress:
        def __init__(self, *, total: int, desc: str, unit: str, disable: bool) -> None:
            self.total = total
            self.desc = desc
            self.unit = unit
            self.disable = disable
            self.updated = 0
            self.closed = False
            self.postfixes: list[str] = []

        def set_postfix_str(self, value: str) -> None:
            self.postfixes.append(value)

        def update(self, step: int) -> None:
            self.updated += step

        def close(self) -> None:
            self.closed = True

    def fake_tqdm(*, total: int, desc: str, unit: str, disable: bool) -> _FakeProgress:
        progress = _FakeProgress(total=total, desc=desc, unit=unit, disable=disable)
        created["progress"] = progress
        return progress

    monkeypatch.setattr(
        "boj_stat_search.catalog.exporter.BojClient", fake_client_factory
    )
    monkeypatch.setattr("boj_stat_search.catalog.exporter.tqdm", fake_tqdm)

    report = generate_metadata_parquet_files(
        output_dir=tmp_path / "metadata",
        dbs=["FM01", "BP01"],
        show_progress=True,
    )

    progress = created["progress"]
    assert progress.total == 2
    assert progress.desc == "Generating metadata Parquet"
    assert progress.unit == "db"
    assert progress.disable is False
    assert progress.updated == 2
    assert progress.closed is True
    assert progress.postfixes[-1] == "BP01: 1 rows"
    assert report.is_success is True
