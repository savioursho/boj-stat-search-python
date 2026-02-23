from typing import Any
import warnings
from urllib.parse import SplitResult, urlencode, urlunsplit

from boj_stat_search.core.types import Code, ErrorMode, Frequency, Layer, Period
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

_VALIDATION_ERROR_MODES: tuple[ErrorMode, ...] = ("raise", "warn", "ignore")

SCHEME = "https"
NETLOC = "www.stat-search.boj.or.jp"
VERSION = "v1"

API_PATH = {
    "getDataCode": f"/api/{VERSION}/getDataCode",
    "getDataLayer": f"/api/{VERSION}/getDataLayer",
    "getMetadata": f"/api/{VERSION}/getMetadata",
}


def _handle_validation_errors(
    validation_errors: list[str],
    on_validation_error: str,
) -> None:
    if on_validation_error not in _VALIDATION_ERROR_MODES:
        raise ValueError(
            "on_validation_error: must be one of 'raise', 'warn', 'ignore'"
        )

    if not validation_errors:
        return

    message = f"Invalid parameters: {'; '.join(validation_errors)}"
    if on_validation_error == "raise":
        raise ValueError(message)
    if on_validation_error == "warn":
        warnings.warn(message, UserWarning, stacklevel=2)


def build_metadata_api_url(
    db: str,
    on_validation_error: ErrorMode = "raise",
) -> str:
    validation_errors = validate_metadata_params(db=db)
    _handle_validation_errors(validation_errors, on_validation_error)

    query = urlencode({"db": db})

    split_result = SplitResult(
        scheme=SCHEME,
        netloc=NETLOC,
        path=API_PATH["getMetadata"],
        query=query,
        fragment="",
    )
    return urlunsplit(split_result)


def build_data_code_api_url(
    db: str | None = None,
    code: Code | str | None = None,
    start_date: Period | str | None = None,
    end_date: Period | str | None = None,
    start_position: int | None = None,
    on_validation_error: ErrorMode = "raise",
) -> str:
    code_embedded_db = extract_db_from_code(code)
    if db is not None and code_embedded_db is not None and db != code_embedded_db:
        raise ValueError("db/code: conflicting DB values between db and Code input")

    resolved_db = db if db is not None else code_embedded_db
    normalized_code: Any = coerce_code(code)
    normalized_start_date: Any = coerce_period(start_date)
    normalized_end_date: Any = coerce_period(end_date)

    validation_errors = validate_data_code_params(
        db=resolved_db,
        code=normalized_code,
        start_date=normalized_start_date,
        end_date=normalized_end_date,
        start_position=start_position,
    )
    _handle_validation_errors(validation_errors, on_validation_error)

    query_params: dict[str, Any] = {}
    if resolved_db is not None:
        query_params["db"] = resolved_db
    query_params["code"] = normalized_code
    if normalized_start_date is not None:
        query_params["startDate"] = normalized_start_date
    if normalized_end_date is not None:
        query_params["endDate"] = normalized_end_date
    if start_position is not None:
        query_params["startPosition"] = start_position

    query = urlencode(query_params, safe=",")

    split_result = SplitResult(
        scheme=SCHEME,
        netloc=NETLOC,
        path=API_PATH["getDataCode"],
        query=query,
        fragment="",
    )
    return urlunsplit(split_result)


def build_data_layer_api_url(
    db: str,
    frequency: Frequency | str,
    layer: Layer | str,
    start_date: Period | str | None = None,
    end_date: Period | str | None = None,
    start_position: int | None = None,
    on_validation_error: ErrorMode = "raise",
) -> str:
    normalized_frequency: Any = coerce_frequency(frequency)
    normalized_layer: Any = coerce_layer(layer)
    normalized_start_date: Any = coerce_period(
        start_date,
        frequency=normalized_frequency,
    )
    normalized_end_date: Any = coerce_period(
        end_date,
        frequency=normalized_frequency,
    )

    validation_errors = validate_data_layer_params(
        db=db,
        frequency=normalized_frequency,
        layer=normalized_layer,
        start_date=normalized_start_date,
        end_date=normalized_end_date,
        start_position=start_position,
    )
    _handle_validation_errors(validation_errors, on_validation_error)

    query_params: dict[str, str | int] = {
        "db": db,
        "frequency": normalized_frequency,
        "layer": normalized_layer,
    }
    if normalized_start_date is not None:
        query_params["startDate"] = normalized_start_date
    if normalized_end_date is not None:
        query_params["endDate"] = normalized_end_date
    if start_position is not None:
        query_params["startPosition"] = start_position

    query = urlencode(query_params, safe=",*")

    split_result = SplitResult(
        scheme=SCHEME,
        netloc=NETLOC,
        path=API_PATH["getDataLayer"],
        query=query,
        fragment="",
    )
    return urlunsplit(split_result)
