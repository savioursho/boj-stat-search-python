from boj_stat_search.client import BojClient
from boj_stat_search.api import (
    BojApiError,
    get_data_code,
    get_data_code_raw,
    get_data_layer,
    get_data_layer_raw,
    get_metadata,
    get_metadata_raw,
)
from boj_stat_search.catalog import MetadataExportReport, generate_metadata_parquet_files
from boj_stat_search.core import Frequency, Layer, Period, list_db
from boj_stat_search.display import show_layers
from boj_stat_search.models import (
    BaseResponse,
    DataResponse,
    DbInfo,
    MetadataEntry,
    MetadataResponse,
)

__all__ = [
    "BojClient",
    "BojApiError",
    "get_metadata_raw",
    "get_metadata",
    "get_data_code_raw",
    "get_data_code",
    "get_data_layer_raw",
    "get_data_layer",
    "generate_metadata_parquet_files",
    "Frequency",
    "Layer",
    "Period",
    "MetadataExportReport",
    "BaseResponse",
    "DbInfo",
    "MetadataEntry",
    "MetadataResponse",
    "DataResponse",
    "list_db",
    "show_layers",
]


def main() -> None:
    from boj_stat_search.cli.app import app

    app()
