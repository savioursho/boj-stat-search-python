from typing import Any

from boj_stat_search.models import MetadataEntry, MetadataResponse


def _parse_metadata_entry(raw: dict[str, Any]) -> MetadataEntry:
    return MetadataEntry(
        series_code=str(raw.get("SERIES_CODE", "")),
        name_of_time_series_j=str(raw.get("NAME_OF_TIME_SERIES_J", "")),
        name_of_time_series=str(raw.get("NAME_OF_TIME_SERIES", "")),
        unit_j=str(raw.get("UNIT_J", "")),
        unit=str(raw.get("UNIT", "")),
        frequency=str(raw.get("FREQUENCY", "")),
        category_j=str(raw.get("CATEGORY_J", "")),
        category=str(raw.get("CATEGORY", "")),
        layer1=int(raw.get("LAYER1", 0)),
        layer2=int(raw.get("LAYER2", 0)),
        layer3=int(raw.get("LAYER3", 0)),
        layer4=int(raw.get("LAYER4", 0)),
        layer5=int(raw.get("LAYER5", 0)),
        start_of_the_time_series=str(raw.get("START_OF_THE_TIME_SERIES", "")),
        end_of_the_time_series=str(raw.get("END_OF_THE_TIME_SERIES", "")),
        last_update=str(raw.get("LAST_UPDATE", "")),
        notes_j=str(raw.get("NOTES_J", "")),
        notes=str(raw.get("NOTES", "")),
    )


def parse_metadata_response(raw: dict[str, Any]) -> MetadataResponse:
    result_set_raw = raw.get("RESULTSET", [])
    result_set = tuple(_parse_metadata_entry(entry) for entry in result_set_raw)

    return MetadataResponse(
        status=int(raw.get("STATUS", 0)),
        message_id=str(raw.get("MESSAGEID", "")),
        message=str(raw.get("MESSAGE", "")),
        date=str(raw.get("DATE", "")),
        db=str(raw.get("DB", "")),
        result_set=result_set,
    )
