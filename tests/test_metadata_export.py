from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from boj_stat_search.catalog import (
    METADATA_CSV_COLUMNS,
    generate_metadata_csvs,
    metadata_entries_to_rows,
    write_metadata_csv,
)
from boj_stat_search.models import MetadataEntry, MetadataResponse


def _make_entry(
    series_code: str,
    *,
    name_j: str = "name-j",
    name_en: str = "name-en",
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
        notes_j="",
        notes="",
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
            _make_entry("STRDCLUCON", name_j="無担保コール", name_en="Call Rate"),
        ),
    )

    assert rows == [
        {
            "db": "FM01",
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
        }
    ]


def test_write_metadata_csv_writes_expected_schema_and_rows(tmp_path: Path) -> None:
    rows = [
        {
            "db": "FM01",
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
        }
    ]
    output = tmp_path / "metadata" / "FM01.csv"

    write_metadata_csv(output, rows)

    header = output.read_text(encoding="utf-8").splitlines()[0]
    assert header == ",".join(METADATA_CSV_COLUMNS)

    with output.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        parsed_rows = list(reader)

    assert len(parsed_rows) == 1
    assert parsed_rows[0]["db"] == "FM01"
    assert parsed_rows[0]["series_code"] == "STRDCLUCON"


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


def test_generate_metadata_csvs_writes_files_and_is_idempotent(
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
    report1 = generate_metadata_csvs(
        output_dir=output_dir,
        dbs=["FM01", "FM01", "BP01"],
        min_request_interval=0.25,
    )

    fm01_csv = output_dir / "FM01.csv"
    bp01_csv = output_dir / "BP01.csv"
    first_fm01_content = fm01_csv.read_text(encoding="utf-8")
    first_bp01_content = bp01_csv.read_text(encoding="utf-8")

    report2 = generate_metadata_csvs(
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

    assert fm01_csv.exists()
    assert bp01_csv.exists()
    assert fm01_csv.read_text(encoding="utf-8") == first_fm01_content
    assert bp01_csv.read_text(encoding="utf-8") == first_bp01_content
    assert report2.is_success is True

    assert len(created_clients) == 2
    assert created_clients[0].min_request_interval == 0.25
    assert created_clients[0].calls == ["FM01", "BP01"]


def test_generate_metadata_csvs_continues_on_failures_and_reports_them(
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
    report = generate_metadata_csvs(output_dir=output_dir, dbs=["FM01", "BP01"])

    assert report.is_success is False
    assert report.succeeded_dbs == ("FM01",)
    assert report.failed_dbs == ("BP01",)
    assert report.row_counts["FM01"] == 1
    assert report.error_messages["BP01"] == "boom"

    assert (output_dir / "FM01.csv").exists()
    assert not (output_dir / "BP01.csv").exists()
