from boj_stat_search.shell.client import BojClient
from boj_stat_search.shell.api import (
    BojApiError,
    get_data_code,
    get_data_code_raw,
    get_data_layer,
    get_data_layer_raw,
    get_metadata,
    get_metadata_raw,
)
from boj_stat_search.shell.catalog.exporter import (
    MetadataExportReport,
    generate_metadata_parquet_files,
)
from boj_stat_search.shell.catalog.loader import (
    CatalogCacheError,
    CatalogError,
    CatalogFetchError,
    load_catalog_all,
    load_catalog_db,
)
from boj_stat_search.shell.catalog.search import (
    list_series,
    resolve_db,
    search_series,
)
from boj_stat_search.core import Code, Frequency, Layer, Period, list_db
from boj_stat_search.shell.display import show_layers
from boj_stat_search.core.models import (
    BaseResponse,
    DataResponse,
    DbInfo,
    MetadataEntry,
    MetadataResponse,
    SeriesCatalogEntry,
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
    "load_catalog_db",
    "load_catalog_all",
    "list_series",
    "search_series",
    "resolve_db",
    "Frequency",
    "Layer",
    "Code",
    "Period",
    "MetadataExportReport",
    "CatalogError",
    "CatalogFetchError",
    "CatalogCacheError",
    "BaseResponse",
    "DbInfo",
    "MetadataEntry",
    "SeriesCatalogEntry",
    "MetadataResponse",
    "DataResponse",
    "list_db",
    "show_layers",
]


def main() -> None:
    from boj_stat_search.shell.cli import app

    app()
