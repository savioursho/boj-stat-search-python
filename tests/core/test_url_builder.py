from typing import cast

import pytest

from boj_stat_search.core.types import Code, ErrorMode, Frequency, Layer, Period
from boj_stat_search.core.url_builder import (
    build_data_code_api_url,
    build_data_layer_api_url,
    build_metadata_api_url,
)


def test_build_metadata_api_url_returns_expected_url():
    db = "IR01"

    result = build_metadata_api_url(db)

    assert result == "https://www.stat-search.boj.or.jp/api/v1/getMetadata?db=IR01"


def test_build_metadata_api_url_raises_on_unknown_db():
    with pytest.raises(ValueError, match="list_db\\(\\)"):
        build_metadata_api_url(db="UNKNOWN")


def test_build_metadata_api_url_warns_and_returns_url_on_invalid_params():
    with pytest.warns(UserWarning, match="Invalid parameters"):
        result = build_metadata_api_url(
            db="UNKNOWN",
            on_validation_error="warn",
        )

    assert result == "https://www.stat-search.boj.or.jp/api/v1/getMetadata?db=UNKNOWN"


def test_build_metadata_api_url_ignores_invalid_params_and_returns_url():
    result = build_metadata_api_url(
        db="UNKNOWN",
        on_validation_error="ignore",
    )

    assert result == "https://www.stat-search.boj.or.jp/api/v1/getMetadata?db=UNKNOWN"


def test_build_metadata_api_url_raises_on_invalid_on_validation_error_mode():
    with pytest.raises(ValueError, match="on_validation_error"):
        build_metadata_api_url(
            db="IR01",
            on_validation_error=cast(ErrorMode, "invalid"),
        )


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


def test_build_data_code_api_url_accepts_period_instances():
    result = build_data_code_api_url(
        db="CO",
        code="TK99F1000601GCQ01000,TK99F2000601GCQ01000",
        start_date=Period.quarter(2024, 1),
        end_date=Period.quarter(2025, 4),
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=CO&code=TK99F1000601GCQ01000,TK99F2000601GCQ01000&startDate=202401&endDate=202504"
    )


def test_build_data_code_api_url_accepts_code_class_with_embedded_db():
    result = build_data_code_api_url(code=Code("FM01'STRDCLUCON"))

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON"
    )


def test_build_data_code_api_url_accepts_code_class_with_multiple_codes():
    result = build_data_code_api_url(code=Code("FM01'A", "FM01'B"))

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=A,B"
    )


def test_build_data_code_api_url_accepts_explicit_db_with_code_class():
    result = build_data_code_api_url(db="FM01", code=Code("STRDCLUCON"))

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON"
    )


def test_build_data_code_api_url_accepts_matching_db_and_embedded_db():
    result = build_data_code_api_url(db="FM01", code=Code("FM01'STRDCLUCON"))

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON"
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


def test_build_data_layer_api_url_accepts_period_instances():
    result = build_data_layer_api_url(
        db="BP01",
        frequency="M",
        layer=Layer(1, 1, 1),
        start_date=Period.month(2025, 4),
        end_date=Period.month(2025, 9),
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=BP01&frequency=M&layer=1,1,1&startDate=202504&endDate=202509"
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


def test_build_data_layer_api_url_accepts_frequency_enum():
    result = build_data_layer_api_url(
        db="MD10",
        frequency=Frequency.QUARTERLY,
        layer="*",
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*"
    )


def test_build_data_layer_api_url_normalizes_lowercase_frequency():
    result = build_data_layer_api_url(db="MD10", frequency="q", layer="*")

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*"
    )


def test_build_data_layer_api_url_accepts_layer_class():
    result = build_data_layer_api_url(
        db="BP01",
        frequency="M",
        layer=Layer(1, 1, 1),
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=BP01&frequency=M&layer=1,1,1"
    )


def test_build_data_layer_api_url_accepts_layer_class_with_wildcard():
    result = build_data_layer_api_url(
        db="MD10",
        frequency="Q",
        layer=Layer("*"),
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*"
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


def test_build_data_layer_api_url_raises_on_invalid_date_granularity_for_frequency():
    with pytest.raises(ValueError, match="start_date"):
        build_data_layer_api_url(
            db="BP01",
            frequency="Q",
            layer="1,1,1",
            start_date=Period.year(2025),
        )


def test_build_data_code_api_url_raises_on_unknown_db():
    with pytest.raises(ValueError, match="list_db\\(\\)"):
        build_data_code_api_url(db="UNKNOWN", code="STRDCLUCON")


def test_build_data_code_api_url_raises_on_conflicting_db_inputs():
    with pytest.raises(ValueError, match="conflicting DB"):
        build_data_code_api_url(db="FM01", code=Code("IR01'STRDCLUCON"))


def test_build_data_code_api_url_raises_on_conflicting_db_inputs_even_when_ignore():
    with pytest.raises(ValueError, match="conflicting DB"):
        build_data_code_api_url(
            db="FM01",
            code=Code("IR01'STRDCLUCON"),
            on_validation_error="ignore",
        )


def test_build_data_layer_api_url_raises_on_unknown_db():
    with pytest.raises(ValueError, match="list_db\\(\\)"):
        build_data_layer_api_url(db="UNKNOWN", frequency="Q", layer="*")


def test_build_data_code_api_url_warns_and_returns_url_on_invalid_params():
    with pytest.warns(UserWarning, match="Invalid parameters"):
        result = build_data_code_api_url(
            db="FM01",
            code="STRDCLUCON",
            start_position=0,
            on_validation_error="warn",
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
        on_validation_error="ignore",
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON&startPosition=0"
    )


def test_build_data_code_api_url_raises_on_invalid_on_validation_error_mode():
    with pytest.raises(ValueError, match="on_validation_error"):
        build_data_code_api_url(
            db="FM01",
            code="STRDCLUCON",
            on_validation_error=cast(ErrorMode, "invalid"),
        )


def test_build_data_layer_api_url_warns_and_returns_url_on_invalid_params():
    with pytest.warns(UserWarning, match="Invalid parameters"):
        result = build_data_layer_api_url(
            db="MD10",
            frequency="X",
            layer="*",
            on_validation_error="warn",
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
        on_validation_error="ignore",
    )

    assert (
        result
        == "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=1,a"
    )


def test_build_data_layer_api_url_raises_on_invalid_on_validation_error_mode():
    with pytest.raises(ValueError, match="on_validation_error"):
        build_data_layer_api_url(
            db="MD10",
            frequency="Q",
            layer="*",
            on_validation_error=cast(ErrorMode, "invalid"),
        )
