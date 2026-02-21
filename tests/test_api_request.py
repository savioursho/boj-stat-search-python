from unittest.mock import Mock

from boj_stat_search.api_request import (
    get_data_code_raw,
    get_metadata,
    get_metadata_raw,
)
from boj_stat_search.models import MetadataEntry, MetadataResponse
from boj_stat_search.url_builder import build_data_code_api_url, build_metadata_api_url


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


def test_get_metadata_uses_client_and_returns_parsed_response():
    db = "IR01"
    expected_url = build_metadata_api_url(db)
    raw_payload = {
        "STATUS": 200,
        "MESSAGEID": "M181000I",
        "MESSAGE": "ok",
        "DATE": "2026-02-21T05:00:12.008+09:00",
        "DB": "IR01",
        "RESULTSET": [
            {
                "SERIES_CODE": "MADR1Z@D",
                "NAME_OF_TIME_SERIES_J": "series jp",
                "NAME_OF_TIME_SERIES": "series en",
                "UNIT_J": "pct_jp",
                "UNIT": "percent per annum",
                "FREQUENCY": "DAILY",
                "CATEGORY_J": "cat jp",
                "CATEGORY": "cat en",
                "LAYER1": 1,
                "LAYER2": 2,
                "LAYER3": 3,
                "LAYER4": 4,
                "LAYER5": 5,
                "START_OF_THE_TIME_SERIES": "19990101",
                "END_OF_THE_TIME_SERIES": "20260221",
                "LAST_UPDATE": "20260221",
                "NOTES_J": "note jp",
                "NOTES": "note en",
            }
        ],
    }

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = raw_payload

    client = Mock()
    client.get.return_value = response

    result = get_metadata(db, client=client)

    client.get.assert_called_once_with(expected_url)
    response.raise_for_status.assert_called_once_with()
    response.json.assert_called_once_with()
    assert result == MetadataResponse(
        status=200,
        message_id="M181000I",
        message="ok",
        date="2026-02-21T05:00:12.008+09:00",
        db="IR01",
        result_set=(
            MetadataEntry(
                series_code="MADR1Z@D",
                name_of_time_series_j="series jp",
                name_of_time_series="series en",
                unit_j="pct_jp",
                unit="percent per annum",
                frequency="DAILY",
                category_j="cat jp",
                category="cat en",
                layer1=1,
                layer2=2,
                layer3=3,
                layer4=4,
                layer5=5,
                start_of_the_time_series="19990101",
                end_of_the_time_series="20260221",
                last_update="20260221",
                notes_j="note jp",
                notes="note en",
            ),
        ),
    )


def test_get_data_code_raw_uses_client_and_returns_json():
    db = "FM01"
    code = "STRDCLUCON,STRACLUCON"
    expected_url = build_data_code_api_url(db=db, code=code)
    expected_payload = {
        "STATUS": 200,
        "MESSAGEID": "M181000I",
        "MESSAGE": "ok",
        "DB": db,
    }

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = expected_payload

    client = Mock()
    client.get.return_value = response

    result = get_data_code_raw(db=db, code=code, client=client)

    client.get.assert_called_once_with(expected_url)
    response.raise_for_status.assert_called_once_with()
    response.json.assert_called_once_with()
    assert result == expected_payload
