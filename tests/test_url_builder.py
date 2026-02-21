import pytest

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


def test_build_data_code_api_url_returns_expected_url_with_optional_params():
    result = build_data_code_api_url(
        db="CO",
        code="TK99F1000601GCQ01000,TK99F2000601GCQ01000",
        start_date="202401",
        end_date="202504",
        start_position=160,
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=CO&code=TK99F1000601GCQ01000,TK99F2000601GCQ01000&startDate=202401&endDate=202504&startPosition=160"
    )


def test_build_data_code_api_url_returns_expected_url_with_partial_optional_params():
    result = build_data_code_api_url(
        db="FM01",
        code="STRDCLUCON",
        start_date="202501",
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON&startDate=202501"
    )


def test_build_data_layer_api_url_returns_expected_url_for_wildcard_layer():
    result = build_data_layer_api_url(db="MD10", frequency="Q", layer="*")

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*"
    )


def test_build_data_layer_api_url_returns_expected_url_with_optional_params():
    result = build_data_layer_api_url(
        db="BP01",
        frequency="M",
        layer="1,1,1",
        start_date="202504",
        end_date="202509",
        start_position=255,
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=BP01&frequency=M&layer=1,1,1&startDate=202504&endDate=202509&startPosition=255"
    )


def test_build_data_layer_api_url_returns_expected_url_with_partial_optional_params():
    result = build_data_layer_api_url(
        db="MD10",
        frequency="Q",
        layer="*",
        start_position=255,
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*&startPosition=255"
    )


def test_build_data_layer_api_url_returns_expected_url_for_comma_layer():
    result = build_data_layer_api_url(db="BP01", frequency="M", layer="1,1,1")

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=BP01&frequency=M&layer=1,1,1"
    )


def test_build_data_code_api_url_raises_on_invalid_start_position():
    with pytest.raises(ValueError, match="start_position"):
        build_data_code_api_url(db="FM01", code="STRDCLUCON", start_position=0)


def test_build_data_code_api_url_raises_on_invalid_date():
    with pytest.raises(ValueError, match="start_date"):
        build_data_code_api_url(db="FM01", code="STRDCLUCON", start_date="202513")


def test_build_data_layer_api_url_raises_on_invalid_frequency():
    with pytest.raises(ValueError, match="frequency"):
        build_data_layer_api_url(db="MD10", frequency="X", layer="*")


def test_build_data_layer_api_url_raises_on_invalid_layer():
    with pytest.raises(ValueError, match="layer"):
        build_data_layer_api_url(db="MD10", frequency="Q", layer="1,a")


def test_build_data_code_api_url_warns_and_returns_url_on_invalid_params():
    with pytest.warns(UserWarning, match="Invalid parameters"):
        result = build_data_code_api_url(
            db="FM01",
            code="STRDCLUCON",
            start_position=0,
            errors="warn",
        )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON&startPosition=0"
    )


def test_build_data_code_api_url_ignores_invalid_params_and_returns_url():
    result = build_data_code_api_url(
        db="FM01",
        code="STRDCLUCON",
        start_position=0,
        errors="ignore",
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON&startPosition=0"
    )


def test_build_data_code_api_url_raises_on_invalid_errors_mode():
    with pytest.raises(ValueError, match="errors"):
        build_data_code_api_url(db="FM01", code="STRDCLUCON", errors="invalid")


def test_build_data_layer_api_url_warns_and_returns_url_on_invalid_params():
    with pytest.warns(UserWarning, match="Invalid parameters"):
        result = build_data_layer_api_url(
            db="MD10",
            frequency="X",
            layer="*",
            errors="warn",
        )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=X&layer=*"
    )


def test_build_data_layer_api_url_ignores_invalid_params_and_returns_url():
    result = build_data_layer_api_url(
        db="MD10",
        frequency="Q",
        layer="1,a",
        errors="ignore",
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=1,a"
    )


def test_build_data_layer_api_url_raises_on_invalid_errors_mode():
    with pytest.raises(ValueError, match="errors"):
        build_data_layer_api_url(
            db="MD10",
            frequency="Q",
            layer="*",
            errors="invalid",
        )
