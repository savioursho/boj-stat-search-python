import httpx
from typing import Any

from boj_stat_search.models import DataResponse, MetadataResponse
from boj_stat_search.core.parser import (
    parse_data_code_response,
    parse_metadata_response,
)
from boj_stat_search.core.types import ErrorMode
from boj_stat_search.core.url_builder import (
    build_data_code_api_url,
    build_data_layer_api_url,
    build_metadata_api_url,
)


def _get_json(url: str, *, client: httpx.Client | None = None) -> dict[str, Any]:
    if client is not None:
        response = client.get(url)
        response.raise_for_status()
        return response.json()

    with httpx.Client() as local_client:
        response = local_client.get(url)
        response.raise_for_status()
        return response.json()


def get_metadata_raw(
    db: str,
    on_validation_error: ErrorMode = "raise",
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    url = build_metadata_api_url(
        db=db,
        on_validation_error=on_validation_error,
    )
    return _get_json(url, client=client)


def get_metadata(
    db: str,
    on_validation_error: ErrorMode = "raise",
    *,
    client: httpx.Client | None = None,
) -> MetadataResponse:
    raw = get_metadata_raw(
        db=db,
        on_validation_error=on_validation_error,
        client=client,
    )
    return parse_metadata_response(raw)


def get_data_code_raw(
    db: str,
    code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
    on_validation_error: ErrorMode = "raise",
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    url = build_data_code_api_url(
        db=db,
        code=code,
        start_date=start_date,
        end_date=end_date,
        start_position=start_position,
        on_validation_error=on_validation_error,
    )
    return _get_json(url, client=client)


def get_data_code(
    db: str,
    code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
    on_validation_error: ErrorMode = "raise",
    *,
    client: httpx.Client | None = None,
) -> DataResponse:
    raw = get_data_code_raw(
        db=db,
        code=code,
        start_date=start_date,
        end_date=end_date,
        start_position=start_position,
        on_validation_error=on_validation_error,
        client=client,
    )
    return parse_data_code_response(raw)


def get_data_layer_raw(
    db: str,
    frequency: str,
    layer: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
    on_validation_error: ErrorMode = "raise",
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    url = build_data_layer_api_url(
        db=db,
        frequency=frequency,
        layer=layer,
        start_date=start_date,
        end_date=end_date,
        start_position=start_position,
        on_validation_error=on_validation_error,
    )
    return _get_json(url, client=client)


def get_data_layer(
    db: str,
    frequency: str,
    layer: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
    on_validation_error: ErrorMode = "raise",
    *,
    client: httpx.Client | None = None,
) -> DataResponse:
    raw = get_data_layer_raw(
        db=db,
        frequency=frequency,
        layer=layer,
        start_date=start_date,
        end_date=end_date,
        start_position=start_position,
        on_validation_error=on_validation_error,
        client=client,
    )
    return parse_data_code_response(raw)
