from urllib.parse import SplitResult, urlencode, urlunsplit

SCHEME = "https"
NETLOC = "www.stat-search.boj.or.jp"
VERSION = "v1"

API_PATH = {
    "getDataCode": f"/api/{VERSION}/getDataCode",
    "getDataLayer": f"/api/{VERSION}/getDataLayer",
    "getMetadata": f"/api/{VERSION}/getMetadata",
}


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
) -> str:
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
) -> str:
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
