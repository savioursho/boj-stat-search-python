from unittest.mock import Mock

from boj_stat_search.api_request import get_metadata_raw
from boj_stat_search.url_builder import build_metadata_api_url


def test_get_metadata_raw_uses_client_and_returns_json():
    db = "IR01"
    expected_url = build_metadata_api_url(db)
    expected_payload = {"status": "ok", "items": [{"code": "foo"}]}

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = expected_payload

    client = Mock()
    client.get.return_value = response

    result = get_metadata_raw(db, client=client)

    client.get.assert_called_once_with(expected_url)
    response.raise_for_status.assert_called_once_with()
    response.json.assert_called_once_with()
    assert result == expected_payload
