from boj_stat_search.models import DataResponse, MetadataEntry, MetadataResponse
from boj_stat_search.parser import parse_data_code_response, parse_metadata_response


def test_parse_metadata_response_parses_normal_payload():
    raw = {
        "STATUS": 200,
        "MESSAGEID": "M181000I",
        "MESSAGE": "ok",
        "DATE": "2026-02-21T05:00:12.008+09:00",
        "DB": "FM02",
        "RESULTSET": [
            {
                "SERIES_CODE": "STRECLCOON",
                "NAME_OF_TIME_SERIES_J": "series jp",
                "NAME_OF_TIME_SERIES": "series en",
                "UNIT_J": "pct_jp",
                "UNIT": "percent per annum",
                "FREQUENCY": "MONTHLY",
                "CATEGORY_J": "category jp",
                "CATEGORY": "category en",
                "LAYER1": 1,
                "LAYER2": 2,
                "LAYER3": 3,
                "LAYER4": 4,
                "LAYER5": 5,
                "START_OF_THE_TIME_SERIES": "196001",
                "END_OF_THE_TIME_SERIES": "202601",
                "LAST_UPDATE": "20260204",
                "NOTES_J": "note jp",
                "NOTES": "note en",
            }
        ],
    }

    result = parse_metadata_response(raw)

    assert result == MetadataResponse(
        status=200,
        message_id="M181000I",
        message="ok",
        date="2026-02-21T05:00:12.008+09:00",
        db="FM02",
        result_set=(
            MetadataEntry(
                series_code="STRECLCOON",
                name_of_time_series_j="series jp",
                name_of_time_series="series en",
                unit_j="pct_jp",
                unit="percent per annum",
                frequency="MONTHLY",
                category_j="category jp",
                category="category en",
                layer1=1,
                layer2=2,
                layer3=3,
                layer4=4,
                layer5=5,
                start_of_the_time_series="196001",
                end_of_the_time_series="202601",
                last_update="20260204",
                notes_j="note jp",
                notes="note en",
            ),
        ),
    )


def test_parse_metadata_response_handles_error_payload_without_db_and_resultset():
    raw = {
        "STATUS": 400,
        "MESSAGEID": "M181001E",
        "MESSAGE": "Invalid input parameters",
        "DATE": "2026-02-21T05:00:12.008+09:00",
    }

    result = parse_metadata_response(raw)

    assert result == MetadataResponse(
        status=400,
        message_id="M181001E",
        message="Invalid input parameters",
        date="2026-02-21T05:00:12.008+09:00",
        db="",
        result_set=(),
    )


def test_parse_data_code_response_parses_normal_payload():
    raw = {
        "STATUS": 200,
        "MESSAGEID": "M181000I",
        "MESSAGE": "ok",
        "DATE": "2026-02-21T15:58:56.071+09:00",
        "PARAMETER": {
            "FORMAT": "",
            "LANG": "EN",
            "DB": "FM01",
            "STARTDATE": "",
            "ENDDATE": "",
            "STARTPOSITION": "",
        },
        "NEXTPOSITION": 255,
        "RESULTSET": [
            {
                "SERIES_CODE": "STRDCLUCON",
                "NAME_OF_TIME_SERIES": "Call Rate, Uncollateralized Overnight",
                "UNIT": "percent per annum",
                "FREQUENCY": "DAILY",
                "CATEGORY": "Call Rate",
                "LAST_UPDATE": 20260220,
                "VALUES": {
                    "SURVEY_DATES": [19980105, 19980106],
                    "VALUES": [0.49, None],
                },
            }
        ],
    }

    result = parse_data_code_response(raw)

    assert result == DataResponse(
        status=200,
        message_id="M181000I",
        message="ok",
        date="2026-02-21T15:58:56.071+09:00",
        parameter={
            "FORMAT": "",
            "LANG": "EN",
            "DB": "FM01",
            "STARTDATE": "",
            "ENDDATE": "",
            "STARTPOSITION": "",
        },
        next_position=255,
        result_set=(
            {
                "SERIES_CODE": "STRDCLUCON",
                "NAME_OF_TIME_SERIES": "Call Rate, Uncollateralized Overnight",
                "UNIT": "percent per annum",
                "FREQUENCY": "DAILY",
                "CATEGORY": "Call Rate",
                "LAST_UPDATE": 20260220,
                "VALUES": {
                    "SURVEY_DATES": [19980105, 19980106],
                    "VALUES": [0.49, None],
                },
            },
        ),
    )


def test_parse_data_code_response_handles_error_payload_with_missing_fields():
    raw = {
        "STATUS": 400,
        "MESSAGEID": "M181001E",
        "MESSAGE": "Invalid input parameters",
        "DATE": "2026-02-21T15:58:56.071+09:00",
    }

    result = parse_data_code_response(raw)

    assert result == DataResponse(
        status=400,
        message_id="M181001E",
        message="Invalid input parameters",
        date="2026-02-21T15:58:56.071+09:00",
        parameter={},
        next_position=None,
        result_set=(),
    )
