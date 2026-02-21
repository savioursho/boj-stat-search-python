from typing import Any


FORBIDDEN_CHARS = ("<", ">", '"', "”", "!", "|", "\\", ";", "'")
ALLOWED_FREQUENCIES = {"CY", "FY", "CH", "FH", "Q", "M", "W", "D"}


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
        return [f"{name}: MM must be between 01 and 12 for frequency {frequency}"], False
    return [], True


def validate_data_code_params(
    db: str,
    code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
) -> list[str]:
    errors: list[str] = []
    errors.extend(_check_common_text("db", db, required=True))
    errors.extend(_check_common_text("code", code, required=True))
    errors.extend(_validate_start_position(start_position))

    if isinstance(code, str) and code != "":
        code_parts = [part.strip() for part in code.split(",")]
        if any(part == "" for part in code_parts):
            errors.append("code: must contain non-empty comma-separated series codes")
        if len(code_parts) > 250:
            errors.append("code: supports at most 250 series codes per request")

    start_date_valid = start_date is None
    end_date_valid = end_date is None
    if start_date is not None:
        start_date_errors, start_date_valid = _validate_date_for_data_code(
            "start_date",
            start_date,
        )
        errors.extend(start_date_errors)
    if end_date is not None:
        end_date_errors, end_date_valid = _validate_date_for_data_code(
            "end_date",
            end_date,
        )
        errors.extend(end_date_errors)

    if (
        start_date is not None
        and end_date is not None
        and start_date_valid
        and end_date_valid
        and isinstance(start_date, str)
        and isinstance(end_date, str)
    ):
        if len(start_date) != len(end_date):
            errors.append(
                "start_date/end_date: must use the same date granularity (both YYYY or both YYYYMM)"
            )
        elif start_date > end_date:
            errors.append("start_date/end_date: start_date must be <= end_date")

    return errors


def validate_data_layer_params(
    db: str,
    frequency: str,
    layer: str,
    start_date: str | None = None,
    end_date: str | None = None,
    start_position: int | None = None,
) -> list[str]:
    errors: list[str] = []
    errors.extend(_check_common_text("db", db, required=True))
    errors.extend(_check_common_text("frequency", frequency, required=True))
    errors.extend(_check_common_text("layer", layer, required=True))
    errors.extend(_validate_start_position(start_position))

    normalized_frequency = ""
    frequency_valid = False
    if isinstance(frequency, str) and frequency != "":
        normalized_frequency = frequency.upper()
        if normalized_frequency not in ALLOWED_FREQUENCIES:
            errors.append(
                "frequency: must be one of CY, FY, CH, FH, Q, M, W, D"
            )
        else:
            frequency_valid = True

    if isinstance(layer, str) and layer != "":
        layer_parts = [part.strip() for part in layer.split(",")]
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

    start_date_valid = start_date is None
    end_date_valid = end_date is None
    if start_date is not None:
        start_date_errors, start_date_valid = _validate_date_for_frequency(
            "start_date",
            start_date,
            normalized_frequency,
        )
        errors.extend(start_date_errors)
    if end_date is not None:
        end_date_errors, end_date_valid = _validate_date_for_frequency(
            "end_date",
            end_date,
            normalized_frequency,
        )
        errors.extend(end_date_errors)

    if (
        start_date is not None
        and end_date is not None
        and frequency_valid
        and start_date_valid
        and end_date_valid
        and isinstance(start_date, str)
        and isinstance(end_date, str)
        and start_date > end_date
    ):
        errors.append("start_date/end_date: start_date must be <= end_date")

    return errors
