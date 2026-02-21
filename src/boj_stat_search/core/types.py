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


ErrorMode = Literal["raise", "warn", "ignore"]
