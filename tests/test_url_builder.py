from boj_stat_search.core.url_builder import (
    build_data_code_api_url,
    build_data_layer_api_url,
    build_metadata_api_url,
)


def test_build_metadata_api_url_returns_expected_url():
    db = "IR01"

    result = build_metadata_api_url(db)

    assert result == "https://www.stat-search.boj.or.jp/api/v1/getMetadata?db=IR01"


def test_build_data_code_api_url_returns_expected_url_for_single_code():
    result = build_data_code_api_url(db="FM01", code="STRDCLUCON")

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON"
    )


def test_build_data_code_api_url_returns_expected_url_for_multiple_codes():
    result = build_data_code_api_url(db="FM01", code="STRDCLUCON,STRACLUCON")

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON,STRACLUCON"
    )


def test_build_data_layer_api_url_returns_expected_url_for_wildcard_layer():
    result = build_data_layer_api_url(db="MD10", frequency="Q", layer="*")

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*"
    )


def test_build_data_layer_api_url_returns_expected_url_for_comma_layer():
    result = build_data_layer_api_url(db="BP01", frequency="M", layer="1,1,1")

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=BP01&frequency=M&layer=1,1,1"
    )
