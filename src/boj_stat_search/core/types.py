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


ErrorMode = Literal["raise", "warn", "ignore"]
