from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class DbInfo:
    name: str
    desc: str
    category: str

@dataclass(frozen=True)
class MetadataEntry:
    series_code: str
    name_of_time_series_j: str
    name_of_time_series: str
    unit_j: str
    unit: str
    frequency: str
    category_j: str
    category: str
    layer1: int
    layer2: int
    layer3: int
    layer4: int
    layer5: int
    start_of_the_time_series: str
    end_of_the_time_series: str
    last_update: str
    notes_j: str
    notes: str


@dataclass(frozen=True)
class BaseResponse:
    status: int
    message_id: str
    message: str
    date: str


@dataclass(frozen=True)
class MetadataResponse(BaseResponse):
    db: str
    result_set: tuple[MetadataEntry, ...]


@dataclass(frozen=True)
class DataResponse(BaseResponse):
    parameter: dict[str, Any]
    next_position: int | None
    result_set: tuple[dict[str, Any], ...]

