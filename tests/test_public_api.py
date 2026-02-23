import boj_stat_search as bss

from boj_stat_search.api import (
    BojApiError as ApiBojApiError,
    get_data_code as api_get_data_code,
    get_data_code_raw as api_get_data_code_raw,
    get_data_layer as api_get_data_layer,
    get_data_layer_raw as api_get_data_layer_raw,
    get_metadata as api_get_metadata,
    get_metadata_raw as api_get_metadata_raw,
)
from boj_stat_search.catalog import (
    CatalogCacheError as CatalogCatalogCacheError,
    CatalogError as CatalogCatalogError,
    CatalogFetchError as CatalogCatalogFetchError,
    MetadataExportReport as CatalogMetadataExportReport,
    generate_metadata_parquet_files as catalog_generate_metadata_parquet_files,
    list_series as catalog_list_series,
    load_catalog_all as catalog_load_catalog_all,
    load_catalog_db as catalog_load_catalog_db,
    search_series as catalog_search_series,
)
from boj_stat_search.core import Code as CoreCode
from boj_stat_search.core import Frequency as CoreFrequency
from boj_stat_search.core import Layer as CoreLayer
from boj_stat_search.core import Period as CorePeriod
from boj_stat_search.display import show_layers as display_show_layers
from boj_stat_search.models import (
    BaseResponse as ModelsBaseResponse,
    DataResponse as ModelsDataResponse,
    MetadataEntry as ModelsMetadataEntry,
    MetadataResponse as ModelsMetadataResponse,
    SeriesCatalogEntry as ModelsSeriesCatalogEntry,
)


def test_top_level_re_exports_functional_api():
    assert bss.BojApiError is ApiBojApiError
    assert bss.get_metadata_raw is api_get_metadata_raw
    assert bss.get_metadata is api_get_metadata
    assert bss.get_data_code_raw is api_get_data_code_raw
    assert bss.get_data_code is api_get_data_code
    assert bss.get_data_layer_raw is api_get_data_layer_raw
    assert bss.get_data_layer is api_get_data_layer
    assert (
        bss.generate_metadata_parquet_files is catalog_generate_metadata_parquet_files
    )
    assert bss.load_catalog_db is catalog_load_catalog_db
    assert bss.load_catalog_all is catalog_load_catalog_all
    assert bss.list_series is catalog_list_series
    assert bss.search_series is catalog_search_series
    assert bss.show_layers is display_show_layers


def test_top_level_re_exports_key_types_and_models():
    assert bss.Frequency is CoreFrequency
    assert bss.Layer is CoreLayer
    assert bss.Code is CoreCode
    assert bss.Period is CorePeriod
    assert bss.MetadataExportReport is CatalogMetadataExportReport
    assert bss.CatalogError is CatalogCatalogError
    assert bss.CatalogFetchError is CatalogCatalogFetchError
    assert bss.CatalogCacheError is CatalogCatalogCacheError
    assert bss.BaseResponse is ModelsBaseResponse
    assert bss.MetadataEntry is ModelsMetadataEntry
    assert bss.SeriesCatalogEntry is ModelsSeriesCatalogEntry
    assert bss.MetadataResponse is ModelsMetadataResponse
    assert bss.DataResponse is ModelsDataResponse


def test_top_level_has_expected_public_symbols():
    expected = {
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
    }
    assert set(bss.__all__) == expected
