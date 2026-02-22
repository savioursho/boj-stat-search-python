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
    MetadataExportReport as CatalogMetadataExportReport,
    generate_metadata_csvs as catalog_generate_metadata_csvs,
)
from boj_stat_search.core import Frequency as CoreFrequency
from boj_stat_search.core import Layer as CoreLayer
from boj_stat_search.core import Period as CorePeriod
from boj_stat_search.display import show_layers as display_show_layers
from boj_stat_search.models import (
    BaseResponse as ModelsBaseResponse,
    DataResponse as ModelsDataResponse,
    MetadataEntry as ModelsMetadataEntry,
    MetadataResponse as ModelsMetadataResponse,
)


def test_top_level_re_exports_functional_api():
    assert bss.BojApiError is ApiBojApiError
    assert bss.get_metadata_raw is api_get_metadata_raw
    assert bss.get_metadata is api_get_metadata
    assert bss.get_data_code_raw is api_get_data_code_raw
    assert bss.get_data_code is api_get_data_code
    assert bss.get_data_layer_raw is api_get_data_layer_raw
    assert bss.get_data_layer is api_get_data_layer
    assert bss.generate_metadata_csvs is catalog_generate_metadata_csvs
    assert bss.show_layers is display_show_layers


def test_top_level_re_exports_key_types_and_models():
    assert bss.Frequency is CoreFrequency
    assert bss.Layer is CoreLayer
    assert bss.Period is CorePeriod
    assert bss.MetadataExportReport is CatalogMetadataExportReport
    assert bss.BaseResponse is ModelsBaseResponse
    assert bss.MetadataEntry is ModelsMetadataEntry
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
        "generate_metadata_csvs",
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
    }
    assert set(bss.__all__) == expected
