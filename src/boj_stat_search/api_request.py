import httpx
from boj_stat_search.models import MetadataResponse
from boj_stat_search.parser import parse_metadata_response
from boj_stat_search.url_builder import build_metadata_api_url


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

