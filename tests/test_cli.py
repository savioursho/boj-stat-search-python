import json
from pathlib import Path
from types import MappingProxyType
from unittest.mock import patch

from typer.testing import CliRunner

from boj_stat_search.shell.catalog import MetadataExportReport
from boj_stat_search.shell.cli import app
from boj_stat_search.core.models import (
    DataResponse,
    DbInfo,
    MetadataEntry,
    MetadataResponse,
)

runner = CliRunner()

_FAKE_DB_LIST = (
    DbInfo(
        name="FM01",
        desc="Uncollateralized Overnight Call Rate",
        category="Financial Markets",
    ),
    DbInfo(name="IR01", desc="Basic Discount Rates", category="Interest Rates"),
)

_FAKE_METADATA_ENTRY = MetadataEntry(
    series_code="FM01'STRDCLUCON",
    name_of_time_series_j="無担保コール翌日物",
    name_of_time_series="Uncollateralized Overnight Call Rate",
    unit_j="% per annum",
    unit="% per annum",
    frequency="D",
    category_j="金融市場",
    category="Financial Markets",
    layer1=1,
    layer2=0,
    layer3=0,
    layer4=0,
    layer5=0,
    start_of_the_time_series="19850701",
    end_of_the_time_series="20250221",
    last_update="20250222",
    notes_j="",
    notes="",
)

_FAKE_METADATA_RESPONSE = MetadataResponse(
    status=0,
    message_id="OK",
    message="OK",
    date="2025-02-22",
    db="FM01",
    result_set=(_FAKE_METADATA_ENTRY,),
)

_FAKE_DATA_RESPONSE = DataResponse(
    status=0,
    message_id="OK",
    message="OK",
    date="2025-02-22",
    parameter={"db": "FM01"},
    next_position=None,
    result_set=({"date": "20250221", "value": "0.227"},),
)

_FAKE_EXPORT_REPORT_SUCCESS = MetadataExportReport(
    output_dir=Path("metadata"),
    requested_dbs=("FM01", "BP01"),
    succeeded_dbs=("FM01", "BP01"),
    failed_dbs=(),
    row_counts=MappingProxyType({"FM01": 12, "BP01": 34}),
    error_messages=MappingProxyType({}),
)

_FAKE_EXPORT_REPORT_FAILURE = MetadataExportReport(
    output_dir=Path("metadata"),
    requested_dbs=("FM01", "BP01"),
    succeeded_dbs=("FM01",),
    failed_dbs=("BP01",),
    row_counts=MappingProxyType({"FM01": 12}),
    error_messages=MappingProxyType({"BP01": "boom"}),
)


class TestListDb:
    def test_output_contains_db_names(self) -> None:
        with patch("boj_stat_search.shell.cli.list_db", return_value=_FAKE_DB_LIST):
            result = runner.invoke(app, ["list-db"])
        assert result.exit_code == 0
        assert "FM01" in result.output
        assert "IR01" in result.output
        assert "Financial Markets" in result.output

    def test_output_contains_descriptions(self) -> None:
        with patch("boj_stat_search.shell.cli.list_db", return_value=_FAKE_DB_LIST):
            result = runner.invoke(app, ["list-db"])
        assert "Uncollateralized Overnight Call Rate" in result.output
        assert "Basic Discount Rates" in result.output


class TestGetMetadata:
    def test_success_json_output(self) -> None:
        with patch(
            "boj_stat_search.shell.cli.get_metadata",
            return_value=_FAKE_METADATA_RESPONSE,
        ):
            result = runner.invoke(app, ["get-metadata", "FM01"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["db"] == "FM01"
        assert data["result_set"][0]["series_code"] == "FM01'STRDCLUCON"

    def test_missing_db_arg(self) -> None:
        result = runner.invoke(app, ["get-metadata"])
        assert result.exit_code != 0


class TestShowLayers:
    def test_success(self) -> None:
        with (
            patch(
                "boj_stat_search.shell.cli.get_metadata",
                return_value=_FAKE_METADATA_RESPONSE,
            ),
            patch("boj_stat_search.shell.cli.show_layers") as mock_show,
        ):
            result = runner.invoke(app, ["show-layers", "FM01"])
        assert result.exit_code == 0
        mock_show.assert_called_once_with(_FAKE_METADATA_RESPONSE.result_set, None)

    def test_with_layer_option(self) -> None:
        with (
            patch(
                "boj_stat_search.shell.cli.get_metadata",
                return_value=_FAKE_METADATA_RESPONSE,
            ),
            patch("boj_stat_search.shell.cli.show_layers") as mock_show,
        ):
            result = runner.invoke(app, ["show-layers", "FM01", "--layer", "1"])
        assert result.exit_code == 0
        mock_show.assert_called_once_with(_FAKE_METADATA_RESPONSE.result_set, "1")


class TestGetDataCode:
    def test_success_json_output(self) -> None:
        with patch(
            "boj_stat_search.shell.cli.get_data_code",
            return_value=_FAKE_DATA_RESPONSE,
        ):
            result = runner.invoke(app, ["get-data-code", "FM01", "FM01'STRDCLUCON"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["parameter"]["db"] == "FM01"

    def test_with_options(self) -> None:
        with patch(
            "boj_stat_search.shell.cli.get_data_code",
            return_value=_FAKE_DATA_RESPONSE,
        ) as mock_fn:
            result = runner.invoke(
                app,
                [
                    "get-data-code",
                    "FM01",
                    "FM01'STRDCLUCON",
                    "--start-date",
                    "2024",
                    "--end-date",
                    "202412",
                    "--start-position",
                    "1",
                ],
            )
        assert result.exit_code == 0
        mock_fn.assert_called_once_with(
            db="FM01",
            code="FM01'STRDCLUCON",
            start_date="2024",
            end_date="202412",
            start_position=1,
        )

    def test_missing_required_args(self) -> None:
        result = runner.invoke(app, ["get-data-code", "FM01"])
        assert result.exit_code != 0


class TestGetDataLayer:
    def test_success_json_output(self) -> None:
        with patch(
            "boj_stat_search.shell.cli.get_data_layer",
            return_value=_FAKE_DATA_RESPONSE,
        ):
            result = runner.invoke(app, ["get-data-layer", "FM01", "D", "1,*"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["result_set"][0]["value"] == "0.227"

    def test_with_options(self) -> None:
        with patch(
            "boj_stat_search.shell.cli.get_data_layer",
            return_value=_FAKE_DATA_RESPONSE,
        ) as mock_fn:
            result = runner.invoke(
                app,
                [
                    "get-data-layer",
                    "FM01",
                    "D",
                    "1,*",
                    "--start-date",
                    "2024",
                    "--end-date",
                    "202412",
                    "--start-position",
                    "1",
                ],
            )
        assert result.exit_code == 0
        mock_fn.assert_called_once_with(
            db="FM01",
            frequency="D",
            layer="1,*",
            start_date="2024",
            end_date="202412",
            start_position=1,
        )

    def test_missing_required_args(self) -> None:
        result = runner.invoke(app, ["get-data-layer", "FM01", "D"])
        assert result.exit_code != 0


class TestGenerateMetadataParquet:
    def test_success(self) -> None:
        with patch(
            "boj_stat_search.shell.cli.generate_metadata_parquet_files",
            return_value=_FAKE_EXPORT_REPORT_SUCCESS,
        ) as mock_fn:
            result = runner.invoke(
                app,
                [
                    "generate-metadata-parquet",
                    "--output-dir",
                    "metadata",
                    "--db",
                    "FM01",
                    "--db",
                    "BP01",
                    "--min-request-interval",
                    "0.2",
                ],
            )

        assert result.exit_code == 0
        mock_fn.assert_called_once_with(
            output_dir="metadata",
            dbs=["FM01", "BP01"],
            min_request_interval=0.2,
            show_progress=True,
        )
        assert "FM01: wrote 12 rows" in result.output
        assert "BP01: wrote 34 rows" in result.output
        assert (
            "Metadata Parquet export completed successfully (2/2 succeeded)."
            in result.output
        )

    def test_failure_exits_non_zero(self) -> None:
        with patch(
            "boj_stat_search.shell.cli.generate_metadata_parquet_files",
            return_value=_FAKE_EXPORT_REPORT_FAILURE,
        ) as mock_fn:
            result = runner.invoke(app, ["generate-metadata-parquet"])

        assert result.exit_code == 1
        mock_fn.assert_called_once_with(
            output_dir="metadata",
            dbs=None,
            min_request_interval=1.0,
            show_progress=True,
        )
        assert "FM01: wrote 12 rows" in result.output
        assert (
            "Metadata Parquet export completed with failures (1/2 succeeded)."
            in result.output
        )
        assert "BP01: boom" in result.output
