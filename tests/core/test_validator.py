import pytest

from boj_stat_search.core.types import Code, Frequency, Layer, Period
from boj_stat_search.core.validator import (
    coerce_code,
    coerce_frequency,
    coerce_layer,
    coerce_period,
    extract_db_from_code,
    validate_data_code_params,
    validate_data_layer_params,
    validate_metadata_params,
)


def _has_error(errors: list[str], text: str) -> bool:
    return any(text in error for error in errors)


def test_validate_data_code_params_accepts_required_fields():
    errors = validate_data_code_params(
        db="FM01",
        code="STRDCLUCON",
    )

    assert errors == []


def test_validate_data_code_params_accepts_optional_fields():
    errors = validate_data_code_params(
        db="CO",
        code="TK99F1000601GCQ01000,TK99F2000601GCQ01000",
        start_date="202401",
        end_date="202504",
        start_position=160,
    )

    assert errors == []


def test_validate_data_code_params_rejects_empty_code_token():
    errors = validate_data_code_params(
        db="FM01",
        code="STRDCLUCON,,STRACLUCON",
    )

    assert _has_error(errors, "non-empty comma-separated series codes")


def test_validate_data_code_params_rejects_too_many_codes():
    code = ",".join(f"S{i}" for i in range(251))

    errors = validate_data_code_params(
        db="FM01",
        code=code,
    )

    assert _has_error(errors, "at most 250")


def test_validate_data_code_params_rejects_invalid_start_position():
    errors = validate_data_code_params(
        db="FM01",
        code="STRDCLUCON",
        start_position=True,
    )

    assert _has_error(errors, "start_position")


def test_validate_data_code_params_rejects_invalid_dates():
    errors = validate_data_code_params(
        db="FM01",
        code="STRDCLUCON",
        start_date="202513",
        end_date="202412",
    )

    assert _has_error(errors, "start_date")


def test_validate_data_code_params_rejects_date_granularity_mismatch():
    errors = validate_data_code_params(
        db="FM01",
        code="STRDCLUCON",
        start_date="2024",
        end_date="202401",
    )

    assert _has_error(errors, "same date granularity")


def test_validate_data_code_params_rejects_unknown_db():
    errors = validate_data_code_params(
        db="UNKNOWN",
        code="STRDCLUCON",
    )

    assert _has_error(errors, "list_db()")


def test_validate_data_layer_params_accepts_valid_q_dates():
    errors = validate_data_layer_params(
        db="BP01",
        frequency="Q",
        layer="1,1,1",
        start_date="202401",
        end_date="202404",
        start_position=1,
    )

    assert errors == []


def test_validate_data_layer_params_accepts_valid_w_dates():
    errors = validate_data_layer_params(
        db="MD10",
        frequency="W",
        layer="*",
        start_date="202501",
        end_date="202512",
    )

    assert errors == []


def test_validate_data_layer_params_rejects_invalid_frequency():
    errors = validate_data_layer_params(
        db="MD10",
        frequency="X",
        layer="*",
    )

    assert _has_error(errors, "must be one of CY, FY, CH, FH, Q, M, W, D")


def test_validate_data_layer_params_rejects_invalid_layer_value():
    errors = validate_data_layer_params(
        db="MD10",
        frequency="Q",
        layer="1,a",
    )

    assert _has_error(errors, "layer")


def test_validate_data_layer_params_rejects_invalid_date_for_frequency():
    errors = validate_data_layer_params(
        db="BP01",
        frequency="Q",
        layer="1,1,1",
        start_date="202405",
    )

    assert _has_error(errors, "QQ")


def test_validate_data_layer_params_rejects_date_order():
    errors = validate_data_layer_params(
        db="BP01",
        frequency="M",
        layer="1,1,1",
        start_date="202512",
        end_date="202501",
    )

    assert _has_error(errors, "start_date must be <=")


def test_validate_data_layer_params_rejects_non_ascii_db():
    errors = validate_data_layer_params(
        db="ＭD10",
        frequency="M",
        layer="*",
    )

    assert _has_error(errors, "ASCII")


def test_validate_data_layer_params_rejects_unknown_db():
    errors = validate_data_layer_params(
        db="UNKNOWN",
        frequency="M",
        layer="*",
    )

    assert _has_error(errors, "list_db()")


def test_coerce_frequency_from_enum_returns_api_code():
    assert coerce_frequency(Frequency.QUARTERLY) == "Q"


def test_coerce_layer_from_layer_returns_api_code():
    assert coerce_layer(Layer(1, 1, 1)) == "1,1,1"


def test_coerce_code_from_code_returns_api_code():
    assert coerce_code(Code("IR01'A", "IR01'B")) == "A,B"


def test_coerce_period_from_period_returns_api_code():
    assert coerce_period(Period.month(2025, 4)) == "202504"


def test_extract_db_from_code_returns_embedded_db():
    assert extract_db_from_code(Code("IR01'A")) == "IR01"


def test_extract_db_from_non_code_returns_none():
    assert extract_db_from_code("A") is None


def test_coerce_period_with_frequency_falls_back_to_raw_value():
    assert coerce_period(Period.year(2025), frequency="Q") == "2025"


def test_validate_data_code_params_accepts_period_instances():
    errors = validate_data_code_params(
        db="FM01",
        code="STRDCLUCON",
        start_date=Period.month(2025, 1),
        end_date=Period.month(2025, 12),
    )

    assert errors == []


def test_validate_data_layer_params_accepts_frequency_enum():
    errors = validate_data_layer_params(
        db="MD10",
        frequency=Frequency.WEEKLY,
        layer="*",
        start_date="202501",
        end_date="202512",
    )

    assert errors == []


def test_validate_data_layer_params_normalizes_lowercase_frequency():
    errors = validate_data_layer_params(
        db="BP01",
        frequency="q",
        layer="1,1,1",
        start_date="202401",
        end_date="202404",
    )

    assert errors == []


def test_validate_data_layer_params_accepts_layer_class():
    errors = validate_data_layer_params(
        db="BP01",
        frequency="Q",
        layer=Layer(1, "*", 3),
        start_date="202401",
        end_date="202404",
    )

    assert errors == []


def test_validate_data_layer_params_accepts_period_instances():
    errors = validate_data_layer_params(
        db="BP01",
        frequency="M",
        layer=Layer(1, 1, 1),
        start_date=Period.month(2025, 4),
        end_date=Period.month(2025, 9),
    )

    assert errors == []


def test_validate_data_layer_params_rejects_daily_yyyymmdd_string():
    errors = validate_data_layer_params(
        db="MD10",
        frequency="D",
        layer="*",
        start_date="20250131",
    )

    assert _has_error(errors, "expected YYYYMM for frequency D")


def test_layer_rejects_empty_levels():
    with pytest.raises(ValueError, match="between 1 and 5"):
        Layer()


def test_layer_rejects_too_many_levels():
    with pytest.raises(ValueError, match="between 1 and 5"):
        Layer(1, 2, 3, 4, 5, 6)


def test_layer_rejects_numeric_string_level():
    with pytest.raises(ValueError, match="int or '\\*'"):
        Layer("1")


def test_layer_rejects_negative_int_level():
    with pytest.raises(ValueError, match=">= 0"):
        Layer(-1)


def test_validate_metadata_params_accepts_known_db():
    errors = validate_metadata_params(db="FM01")

    assert errors == []


def test_validate_metadata_params_rejects_unknown_db():
    errors = validate_metadata_params(db="UNKNOWN")

    assert _has_error(errors, "list_db()")
