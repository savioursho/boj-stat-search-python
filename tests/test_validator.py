from boj_stat_search.core.validator import (
    validate_data_code_params,
    validate_data_layer_params,
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
