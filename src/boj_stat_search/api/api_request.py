import httpx
from typing import Any

from boj_stat_search.models import DataResponse, MetadataResponse
from boj_stat_search.core.parser import (
    parse_data_code_response,
    parse_metadata_response,
)
from boj_stat_search.core.types import ErrorMode, Frequency
from boj_stat_search.core.url_builder import (
    build_data_code_api_url,
    build_data_layer_api_url,
    build_metadata_api_url,
)


class BojApiError(httpx.HTTPStatusError):
    def __init__(
        self,
        message: str,
        *,
        request: httpx.Request,
        response: httpx.Response,
        boj_status: int | None = None,
        message_id: str | None = None,
        boj_message: str | None = None,
    ) -> None:
        super().__init__(message, request=request, response=response)
        self.boj_status = boj_status
        self.message_id = message_id
        self.boj_message = boj_message


def _extract_error_fields(
    response: httpx.Response,
) -> tuple[int | None, str | None, str | None]:
    try:
        payload = response.json()
    except ValueError:
        return None, None, None

    if not isinstance(payload, dict):
        return None, None, None

    raw_status = payload.get("STATUS")
    if raw_status in (None, ""):
        boj_status = None
    else:
        try:
            boj_status = int(raw_status)
        except (TypeError, ValueError):
            boj_status = None

    raw_message_id = payload.get("MESSAGEID")
    message_id = str(raw_message_id) if raw_message_id not in (None, "") else None

    raw_message = payload.get("MESSAGE")
    boj_message = str(raw_message) if raw_message not in (None, "") else None

    return boj_status, message_id, boj_message


def _raise_for_status_with_boj_message(response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        boj_status, message_id, boj_message = _extract_error_fields(response)
        if boj_status is None and message_id is None and boj_message is None:
            raise

        fragments = [f"HTTP {response.status_code} BOJ API error"]
        if boj_status is not None:
            fragments.append(f"status={boj_status}")
        if message_id is not None:
            fragments.append(f"message_id={message_id}")
        if boj_message is not None:
            fragments.append(f"message={boj_message}")

        raise BojApiError(
            ", ".join(fragments),
            request=exc.request,
            response=exc.response,
            boj_status=boj_status,
            message_id=message_id,
            boj_message=boj_message,
        ) from exc


def _get_json(url: str, *, client: httpx.Client | None = None) -> dict[str, Any]:
    if client is not None:
        response = client.get(url)
        _raise_for_status_with_boj_message(response)
        return response.json()

    with httpx.Client() as local_client:
        response = local_client.get(url)
        _raise_for_status_with_boj_message(response)
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
    frequency: Frequency | str,
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
    frequency: Frequency | str,
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
