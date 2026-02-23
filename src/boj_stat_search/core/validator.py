from typing import Any

from boj_stat_search.core.database import list_db
from boj_stat_search.core.types import Code, Frequency, Layer, Period


FORBIDDEN_CHARS = ("<", ">", '"', "”", "!", "|", "\\", ";", "'")
ALLOWED_FREQUENCIES = {frequency.value for frequency in Frequency}
VALID_DB_NAMES = {db_info.name for db_info in list_db()}


def coerce_frequency(frequency: Any) -> Any:
    if isinstance(frequency, Frequency):
        return frequency.value
    if isinstance(frequency, str):
        return frequency.strip().upper()
    return frequency


def coerce_layer(layer: Any) -> Any:
    if isinstance(layer, Layer):
        return layer.to_api_value()
    return layer


def coerce_code(code: Any) -> Any:
    if isinstance(code, Code):
        return code.to_api_value()
    return code


def extract_db_from_code(code: Any) -> str | None:
    if isinstance(code, Code):
        return code.db
    return None


def coerce_period(
    period: Any,
    *,
    frequency: Frequency | str | None = None,
) -> Any:
    if isinstance(period, Period):
        if frequency is not None:
            try:
                return period.to_api_value(frequency)
            except ValueError:
                return period.to_api_value()
        return period.to_api_value()
    return period


def _check_common_text(
    name: str,
    value: Any,
    *,
    required: bool,
) -> list[str]:
    if value is None:
        if required:
            return [f"{name}: must not be empty"]
        return []

    if not isinstance(value, str):
        return [f"{name}: must be a string"]

    if value == "":
        return [f"{name}: must not be empty"]

    errors: list[str] = []
    if not value.isascii():
        errors.append(f"{name}: must contain only ASCII characters")

    for char in FORBIDDEN_CHARS:
        if char in value:
            errors.append(f"{name}: contains forbidden character '{char}'")
            break

    return errors


def _validate_start_position(start_position: Any) -> list[str]:
    if start_position is None:
        return []
    if isinstance(start_position, bool) or not isinstance(start_position, int):
        return ["start_position: must be an integer >= 1"]
    if start_position < 1:
        return ["start_position: must be an integer >= 1"]
    return []


def _validate_db_name(db: Any) -> list[str]:
    errors = _check_common_text("db", db, required=True)
    if errors:
        return errors

    assert isinstance(db, str)
    if db not in VALID_DB_NAMES:
        return ["db: must be one of known DB names in list_db()"]
    return []


def _validate_date_for_data_code(name: str, value: Any) -> tuple[list[str], bool]:
    errors = _check_common_text(name, value, required=False)
    if errors:
        return errors, False

    assert isinstance(value, str)
    if not value.isdigit():
        return [f"{name}: must contain only digits"], False
    if len(value) not in (4, 6):
        return [f"{name}: expected YYYY or YYYYMM"], False
    if len(value) == 6:
        value_tail = int(value[4:])
        if value_tail < 1 or value_tail > 12:
            return [f"{name}: last two digits must be between 01 and 12"], False
    return [], True


def _validate_date_for_frequency(
    name: str,
    value: Any,
    frequency: str,
) -> tuple[list[str], bool]:
    errors = _check_common_text(name, value, required=False)
    if errors:
        return errors, False

    if frequency not in ALLOWED_FREQUENCIES:
        return [], False

    assert isinstance(value, str)
    if not value.isdigit():
        return [f"{name}: must contain only digits"], False

    if frequency in {"CY", "FY"}:
        if len(value) != 4:
            return [f"{name}: expected YYYY for frequency {frequency}"], False
        return [], True

    if len(value) != 6:
        return [f"{name}: expected YYYYMM for frequency {frequency}"], False

    value_tail = int(value[4:])
    if frequency in {"CH", "FH"}:
        if value_tail not in (1, 2):
            return [f"{name}: HH must be 01 or 02 for frequency {frequency}"], False
        return [], True

    if frequency == "Q":
        if value_tail < 1 or value_tail > 4:
            return [f"{name}: QQ must be between 01 and 04 for frequency Q"], False
        return [], True

    if value_tail < 1 or value_tail > 12:
        return [
            f"{name}: MM must be between 01 and 12 for frequency {frequency}"
        ], False
    return [], True


def validate_data_code_params(
    db: str | None,
    code: str | None,
    start_date: Period | str | None = None,
    end_date: Period | str | None = None,
    start_position: int | None = None,
) -> list[str]:
    normalized_start_date: Any = coerce_period(start_date)
    normalized_end_date: Any = coerce_period(end_date)

    errors: list[str] = []
    errors.extend(_validate_db_name(db))
    errors.extend(_check_common_text("code", code, required=True))
    errors.extend(_validate_start_position(start_position))

    if isinstance(code, str) and code != "":
        code_parts = [part.strip() for part in code.split(",")]
        if any(part == "" for part in code_parts):
            errors.append("code: must contain non-empty comma-separated series codes")
        if len(code_parts) > 250:
            errors.append("code: supports at most 250 series codes per request")

    start_date_valid = normalized_start_date is None
    end_date_valid = normalized_end_date is None
    if normalized_start_date is not None:
        start_date_errors, start_date_valid = _validate_date_for_data_code(
            "start_date",
            normalized_start_date,
        )
        errors.extend(start_date_errors)
    if normalized_end_date is not None:
        end_date_errors, end_date_valid = _validate_date_for_data_code(
            "end_date",
            normalized_end_date,
        )
        errors.extend(end_date_errors)

    if (
        normalized_start_date is not None
        and normalized_end_date is not None
        and start_date_valid
        and end_date_valid
        and isinstance(normalized_start_date, str)
        and isinstance(normalized_end_date, str)
    ):
        if len(normalized_start_date) != len(normalized_end_date):
            errors.append(
                "start_date/end_date: must use the same date granularity (both YYYY or both YYYYMM)"
            )
        elif normalized_start_date > normalized_end_date:
            errors.append("start_date/end_date: start_date must be <= end_date")

    return errors


def validate_metadata_params(
    db: str,
) -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_db_name(db))
    return errors


def validate_data_layer_params(
    db: str,
    frequency: Frequency | str,
    layer: Layer | str,
    start_date: Period | str | None = None,
    end_date: Period | str | None = None,
    start_position: int | None = None,
) -> list[str]:
    normalized_frequency = coerce_frequency(frequency)
    normalized_layer = coerce_layer(layer)
    normalized_start_date = coerce_period(
        start_date,
        frequency=normalized_frequency,
    )
    normalized_end_date = coerce_period(
        end_date,
        frequency=normalized_frequency,
    )

    errors: list[str] = []
    errors.extend(_validate_db_name(db))
    errors.extend(_check_common_text("frequency", normalized_frequency, required=True))
    errors.extend(_check_common_text("layer", normalized_layer, required=True))
    errors.extend(_validate_start_position(start_position))

    frequency_valid = False
    if isinstance(normalized_frequency, str) and normalized_frequency != "":
        if normalized_frequency not in ALLOWED_FREQUENCIES:
            errors.append("frequency: must be one of CY, FY, CH, FH, Q, M, W, D")
        else:
            frequency_valid = True

    if isinstance(normalized_layer, str) and normalized_layer != "":
        layer_parts = [part.strip() for part in normalized_layer.split(",")]
        if len(layer_parts) < 1 or len(layer_parts) > 5:
            errors.append("layer: must have between 1 and 5 comma-separated values")
        if any(part == "" for part in layer_parts):
            errors.append("layer: must not contain empty layer values")
        for part in layer_parts:
            if part == "":
                continue
            if part != "*" and not part.isdigit():
                errors.append("layer: each layer must be '*' or digits only")
                break

    start_date_valid = normalized_start_date is None
    end_date_valid = normalized_end_date is None
    if normalized_start_date is not None:
        start_date_errors, start_date_valid = _validate_date_for_frequency(
            "start_date",
            normalized_start_date,
            str(normalized_frequency),
        )
        errors.extend(start_date_errors)
    if normalized_end_date is not None:
        end_date_errors, end_date_valid = _validate_date_for_frequency(
            "end_date",
            normalized_end_date,
            str(normalized_frequency),
        )
        errors.extend(end_date_errors)

    if (
        normalized_start_date is not None
        and normalized_end_date is not None
        and frequency_valid
        and start_date_valid
        and end_date_valid
        and isinstance(normalized_start_date, str)
        and isinstance(normalized_end_date, str)
        and normalized_start_date > normalized_end_date
    ):
        errors.append("start_date/end_date: start_date must be <= end_date")

    return errors
