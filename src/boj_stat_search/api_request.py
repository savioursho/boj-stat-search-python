import httpx
from boj_stat_search.models import MetadataResponse, DataCodeResponse
from boj_stat_search.parser import parse_data_code_response, parse_metadata_response
from boj_stat_search.url_builder import (
    build_data_code_api_url,
    build_data_layer_api_url,
    build_metadata_api_url,
)


def get_metadata_raw(db: str, *, client: httpx.Client | None = None) -> dict:
    url = build_metadata_api_url(db)

    if client is not None:
        response = client.get(url)
        response.raise_for_status()
        return response.json()

    with httpx.Client() as local_client:
        response = local_client.get(url)
        response.raise_for_status()
        return response.json()

def get_metadata(db: str, *, client: httpx.Client | None = None) -> MetadataResponse:
    raw = get_metadata_raw(db, client=client)
    return parse_metadata_response(raw)

def get_data_code_raw(db: str, code: str, *, client: httpx.Client | None = None) -> dict:
    url = build_data_code_api_url(db, code)

    if client is not None:
        response = client.get(url)
        response.raise_for_status()
        return response.json()

    with httpx.Client() as local_client:
        response = local_client.get(url)
        response.raise_for_status()
        return response.json()

def get_data_code(db: str, code: str, *, client: httpx.Client | None = None) -> DataCodeResponse:
    raw = get_data_code_raw(db=db, code=code, client=client)
    return parse_data_code_response(raw)


def get_data_layer_raw(
    db: str,
    frequency: str,
    layer: str,
    *,
    client: httpx.Client | None = None,
) -> dict:
    url = build_data_layer_api_url(db=db, frequency=frequency, layer=layer)

    if client is not None:
        response = client.get(url)
        response.raise_for_status()
        return response.json()

    with httpx.Client() as local_client:
        response = local_client.get(url)
        response.raise_for_status()
        return response.json()


def get_data_layer(
    db: str,
    frequency: str,
    layer: str,
    *,
    client: httpx.Client | None = None,
) -> DataCodeResponse:
    raw = get_data_layer_raw(
        db=db,
        frequency=frequency,
        layer=layer,
        client=client,
    )
    return parse_data_code_response(raw)
