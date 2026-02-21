import warnings
from typing import Literal
from urllib.parse import SplitResult, urlencode, urlunsplit

from boj_stat_search.core.validator import (
    validate_data_code_params,
    validate_data_layer_params,
)

ErrorMode = Literal["raise", "warn", "ignore"]
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
    errors: str,
) -> None:
    if errors not in _VALIDATION_ERROR_MODES:
        raise ValueError("errors: must be one of 'raise', 'warn', 'ignore'")

    if not validation_errors:
        return

    message = f"Invalid parameters: {'; '.join(validation_errors)}"
    if errors == "raise":
        raise ValueError(message)
    if errors == "warn":
        warnings.warn(message, UserWarning, stacklevel=2)


def build_metadata_api_url(db: str) -> str:
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
    db: str,
    code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
    errors: ErrorMode = "raise",
) -> str:
    validation_errors = validate_data_code_params(
        db=db,
        code=code,
        start_date=start_date,
        end_date=end_date,
        start_position=start_position,
    )
    _handle_validation_errors(validation_errors, errors)

    query_params: dict[str, str | int] = {"db": db, "code": code}
    if start_date is not None:
        query_params["startDate"] = start_date
    if end_date is not None:
        query_params["endDate"] = end_date
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
    frequency: str,
    layer: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
    errors: ErrorMode = "raise",
) -> str:
    validation_errors = validate_data_layer_params(
        db=db,
        frequency=frequency,
        layer=layer,
        start_date=start_date,
        end_date=end_date,
        start_position=start_position,
    )
    _handle_validation_errors(validation_errors, errors)

    query_params: dict[str, str | int] = {
        "db": db,
        "frequency": frequency,
        "layer": layer,
    }
    if start_date is not None:
        query_params["startDate"] = start_date
    if end_date is not None:
        query_params["endDate"] = end_date
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
