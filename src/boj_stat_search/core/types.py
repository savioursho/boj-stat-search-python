from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class Frequency(StrEnum):
    CALENDAR_YEAR = "CY"
    FISCAL_YEAR = "FY"
    CALENDAR_HALF = "CH"
    FISCAL_HALF = "FH"
    QUARTERLY = "Q"
    MONTHLY = "M"
    WEEKLY = "W"
    DAILY = "D"


@dataclass(frozen=True, slots=True, init=False)
class Layer:
    _levels: tuple[str, ...]

    def __init__(self, *levels: int | str) -> None:
        if len(levels) < 1 or len(levels) > 5:
            raise ValueError("layer: must have between 1 and 5 levels")

        normalized_levels: list[str] = []
        for level in levels:
            if isinstance(level, bool):
                raise ValueError("layer: each level must be an int or '*'")
            if isinstance(level, int):
                if level < 0:
                    raise ValueError("layer: integer level must be >= 0")
                normalized_levels.append(str(level))
                continue
            if isinstance(level, str) and level == "*":
                normalized_levels.append(level)
                continue
            raise ValueError("layer: each level must be an int or '*'")

        object.__setattr__(self, "_levels", tuple(normalized_levels))

    @property
    def levels(self) -> tuple[str, ...]:
        return self._levels

    def to_api_value(self) -> str:
        return ",".join(self._levels)

    def __str__(self) -> str:
        return self.to_api_value()


@dataclass(frozen=True, slots=True, init=False)
class Period:
    _value: str

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("period: must be a string")
        if not value.isdigit():
            raise ValueError("period: must contain only digits")
        if len(value) not in (4, 6):
            raise ValueError("period: expected YYYY or YYYYMM-like six-digit value")
        if len(value) == 6:
            tail = int(value[4:])
            if tail < 1 or tail > 12:
                raise ValueError("period: last two digits must be between 01 and 12")
        object.__setattr__(self, "_value", value)

    @classmethod
    def from_string(cls, value: str) -> "Period":
        return cls(value)

    @classmethod
    def year(cls, year: int) -> "Period":
        _validate_year(year)
        return cls(f"{year:04d}")

    @classmethod
    def half(cls, year: int, half: int) -> "Period":
        _validate_year(year)
        _validate_component("half", half, 1, 2)
        return cls(f"{year:04d}{half:02d}")

    @classmethod
    def quarter(cls, year: int, quarter: int) -> "Period":
        _validate_year(year)
        _validate_component("quarter", quarter, 1, 4)
        return cls(f"{year:04d}{quarter:02d}")

    @classmethod
    def month(cls, year: int, month: int) -> "Period":
        _validate_year(year)
        _validate_component("month", month, 1, 12)
        return cls(f"{year:04d}{month:02d}")

    @property
    def value(self) -> str:
        return self._value

    def to_api_value(self, frequency: Frequency | str | None = None) -> str:
        if frequency is None:
            return self._value

        normalized_frequency = (
            frequency.value
            if isinstance(frequency, Frequency)
            else frequency.strip().upper()
            if isinstance(frequency, str)
            else frequency
        )
        if normalized_frequency not in {item.value for item in Frequency}:
            raise ValueError("frequency: must be one of CY, FY, CH, FH, Q, M, W, D")

        if normalized_frequency in {"CY", "FY"}:
            if len(self._value) != 4:
                raise ValueError(
                    f"period: expected YYYY for frequency {normalized_frequency}"
                )
            return self._value

        if len(self._value) != 6:
            raise ValueError(
                f"period: expected YYYYMM-like six-digit value for frequency {normalized_frequency}"
            )

        tail = int(self._value[4:])
        if normalized_frequency in {"CH", "FH"}:
            if tail not in (1, 2):
                raise ValueError(
                    f"period: HH must be 01 or 02 for frequency {normalized_frequency}"
                )
            return self._value
        if normalized_frequency == "Q":
            if tail < 1 or tail > 4:
                raise ValueError("period: QQ must be between 01 and 04 for frequency Q")
            return self._value
        if tail < 1 or tail > 12:
            raise ValueError(
                f"period: MM must be between 01 and 12 for frequency {normalized_frequency}"
            )
        return self._value

    def __str__(self) -> str:
        return self._value


def _validate_year(year: int) -> None:
    if isinstance(year, bool) or not isinstance(year, int):
        raise ValueError("period: year must be an integer in range 1000..9999")
    if year < 1000 or year > 9999:
        raise ValueError("period: year must be an integer in range 1000..9999")


def _validate_component(name: str, value: int, min_value: int, max_value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"period: {name} must be an integer")
    if value < min_value or value > max_value:
        raise ValueError(
            f"period: {name} must be between {min_value:02d} and {max_value:02d}"
        )


ErrorMode = Literal["raise", "warn", "ignore"]
