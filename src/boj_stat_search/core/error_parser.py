from typing import Any, NamedTuple


class BojErrorFields(NamedTuple):
    boj_status: int | None
    message_id: str | None
    boj_message: str | None


def parse_error_payload(payload: dict[str, Any]) -> BojErrorFields:
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

    return BojErrorFields(
        boj_status=boj_status,
        message_id=message_id,
        boj_message=boj_message,
    )
